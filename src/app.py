"""Ứng dụng so sánh Chatbot baseline và ReAct Agent có guardrails."""

from __future__ import annotations

import ast
import argparse
import inspect
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import perf_counter
from typing import Any
from uuid import uuid4

from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from prompts import (  # noqa: E402
    CHATBOT_BASELINE_PROMPT,
    MAX_ITERATIONS,
    REACT_SYSTEM_PROMPT,
    TIMEOUT_SECONDS,
)
from providers import BaseLLMProvider, get_llm_provider  # noqa: E402
from tools import (  # noqa: E402
    AVAILABLE_TOOLS,
    TOOL_SPECS,
    contains_sensitive_data,
)

load_dotenv()

ACTION_RE = re.compile(
    r"^\s*Action\s*:\s*([A-Za-z_]\w*)\s*\[(.*)\]\s*$",
    flags=re.IGNORECASE | re.MULTILINE,
)
FINAL_RE = re.compile(
    r"^\s*Final Answer\s*:\s*(.+(?:\n(?!\s*(?:Thought|Action|Observation)\s*:).*)*)",
    flags=re.IGNORECASE | re.MULTILINE,
)
TOOL_INJECTION_RE = re.compile(
    r"(?:ignore (?:all |the )?(?:previous|system)|bo qua (?:tat ca )?"
    r"(?:chi dan|quy tac|system)|system prompt|developer message|"
    r"\bAction\s*:|api[_ -]?key|password)",
    flags=re.IGNORECASE,
)
USER_INJECTION_RE = re.compile(
    r"(?:ignore (?:all |the )?(?:previous|system) instructions?|"
    r"(?:bo qua|bỏ qua) (?:tat ca |tất cả )?(?:chi dan|chỉ dẫn|quy tac|quy tắc|guardrails?)|"
    r"(?:vo hieu hoa|vô hiệu hóa) (?:guardrails?|quy tac|quy tắc)|you are now)",
    flags=re.IGNORECASE,
)
SYSTEM_SECRET_RE = re.compile(
    r"(?:system prompt|developer message|api[_ -]?key|"
    r"gemini_api_key|openai_api_key|anthropic_api_key|openrouter_api_key)",
    flags=re.IGNORECASE,
)
DISCRIMINATION_RE = re.compile(
    r"(?:khong tuyen|loai|cam)\s+(?:phu nu|nu gioi|nam gioi|nguoi khuyet tat|"
    r"nguoi dan toc|nguoi theo dao)",
    flags=re.IGNORECASE,
)
FABRICATION_RE = re.compile(
    r"(?:bịa|fabricate|invent).*(?:lương|tuyển dụng|việc làm|chứng chỉ|salary)",
    flags=re.IGNORECASE,
)


@dataclass
class AgentResult:
    """Kết quả có cấu trúc để vừa in demo vừa phục vụ kiểm thử/đánh giá."""

    answer: str
    trace: list[str] = field(default_factory=list)
    tool_calls: int = 0
    iterations: int = 0
    guardrail_triggered: bool = False
    route: str = "unknown"
    request_id: str = ""
    trace_log: list[dict[str, Any]] = field(default_factory=list)
    agentic_fit: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AgenticFit:
    """Ma tran 6 tieu chi, moi tieu chi 0-2 theo de bai OreoAI."""

    updated_data: int
    external_data: int
    multi_step: int
    dynamic_tool_choice: int
    observation_dependency: int
    hallucination_risk: int

    @property
    def total(self) -> int:
        return sum(
            (
                self.updated_data,
                self.external_data,
                self.multi_step,
                self.dynamic_tool_choice,
                self.observation_dependency,
                self.hallucination_risk,
            )
        )

    @property
    def recommendation(self) -> str:
        if self.total <= 4:
            return "chatbot"
        if self.total <= 8:
            return "hybrid"
        return "react"

    def as_dict(self) -> dict[str, Any]:
        return {
            "updated_data": self.updated_data,
            "external_data": self.external_data,
            "multi_step": self.multi_step,
            "dynamic_tool_choice": self.dynamic_tool_choice,
            "observation_dependency": self.observation_dependency,
            "hallucination_risk": self.hallucination_risk,
            "total": self.total,
            "recommendation": self.recommendation,
        }


@dataclass(frozen=True)
class RouteDecision:
    route: str
    reason: str
    fit: AgenticFit
    missing_fields: tuple[str, ...] = ()
    guardrail_code: str | None = None


@dataclass(frozen=True)
class ToolExecution:
    observation: str
    status: str
    latency_ms: int
    retry_count: int
    error_code: str | None = None


def load_test_cases(*, include_extended: bool = False) -> list[dict[str, Any]]:
    """Đọc test; mặc định giữ đúng 17 behavioral case của CLI cũ."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "config", "test_cases.json")
    with open(path, "r", encoding="utf-8") as file:
        cases = json.load(file)
    if not isinstance(cases, list) or not cases:
        raise ValueError("config/test_cases.json phải là một danh sách không rỗng.")
    required = {"id", "category", "question", "expected_behavior"}
    for case in cases:
        if not isinstance(case, dict) or not required.issubset(case):
            raise ValueError(f"Test case không hợp lệ: {case!r}")
    if include_extended:
        return cases
    return [case for case in cases if not case.get("test_type")]


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def _redact_value(value: Any) -> Any:
    """Chi log tham so tool da che; khong log nguyen van user query."""
    if not isinstance(value, str):
        return value
    if contains_sensitive_data(value):
        return "[REDACTED_SENSITIVE]"
    redacted = re.sub(
        r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b",
        "[REDACTED_EMAIL]",
        value,
    )
    redacted = re.sub(r"\b(?:\+?84|0)\d{8,10}\b", "[REDACTED_PHONE]", redacted)
    redacted = re.sub(r"\b\d{12}\b", "[REDACTED_ID]", redacted)
    redacted = re.sub(r"\bsk-[A-Za-z0-9_-]{12,}\b", "[REDACTED_SECRET]", redacted)
    return redacted[:100]


def _trace_event(
    *,
    request_id: str,
    route: str,
    selected_tool: str | None,
    tool_input: list[Any] | None,
    tool_status: str,
    latency_ms: int,
    retry_count: int,
    error_code: str | None,
    final_status: str,
) -> dict[str, Any]:
    """Trace chi gom cac truong quan sat duoc theo hop dong cua Lab."""
    return {
        "request_id": request_id,
        "timestamp": _utc_timestamp(),
        "route": route,
        "selected_tool": selected_tool,
        "tool_input": (
            {"args": [_redact_value(value) for value in tool_input]}
            if tool_input is not None
            else None
        ),
        "tool_status": tool_status,
        "latency_ms": max(0, latency_ms),
        "retry_count": retry_count,
        "error_code": error_code,
        "final_status": final_status,
    }


def evaluate_agentic_fit(user_query: str) -> AgenticFit:
    """Cham Agentic Fit 0-2/tieu chi ma khong co tinh day diem len."""
    text = user_query.casefold()
    dynamic_terms = (
        "hiện nay",
        "hiện tại",
        "đang có",
        "mới nhất",
        "tuyển dụng",
        "việc làm",
        "thực tập",
        "mức lương",
        "lương trung bình",
        "chứng chỉ còn hiệu lực",
    )
    market_terms = (
        "tuyển dụng",
        "việc làm",
        "thực tập",
        "mức lương",
        "lương trung bình",
        "thị trường",
        "chứng chỉ",
    )
    multi_terms = (
        "lộ trình",
        "roadmap",
        "phân tích hồ sơ",
        "đánh giá mức độ phù hợp",
        "so sánh",
        "đối chiếu",
        "kế hoạch",
    )
    requires_updated = any(term in text for term in dynamic_terms)
    requires_external = any(term in text for term in market_terms)
    multi_count = sum(term in text for term in multi_terms)
    asks_multiple_outputs = any(
        term in text
        for term in (
            "và lộ trình",
            "và kỹ năng",
            "những kỹ năng",
            "và mức lương",
            "rồi đề xuất",
            "nhiều nghề",
            "3 nghề",
        )
    )
    is_multi_step = multi_count > 0 or asks_multiple_outputs
    needs_observation = requires_external and (is_multi_step or asks_multiple_outputs)
    high_risk = any(
        term in text
        for term in ("mức lương", "lương trung bình", "đang tuyển", "đang có", "chứng chỉ")
    )

    return AgenticFit(
        updated_data=2 if requires_updated else 0,
        external_data=2 if requires_external else 0,
        multi_step=2 if (is_multi_step and asks_multiple_outputs) else int(is_multi_step),
        dynamic_tool_choice=(
            2 if requires_external and is_multi_step else int(requires_external)
        ),
        observation_dependency=2 if needs_observation else int(requires_external),
        hallucination_risk=2 if high_risk else int(requires_external),
    )


def detect_missing_information(user_query: str) -> tuple[str, ...]:
    """Chi chan cac thieu sot thiet yeu; khong ep hoi them khi co the neu gia dinh."""
    text = user_query.casefold()
    missing: list[str] = []
    asks_jobs = any(term in text for term in ("tìm việc", "việc làm", "tuyển dụng", "thực tập"))
    has_location = any(
        term in text
        for term in ("hà nội", "ha noi", "tp.hcm", "hồ chí minh", "đà nẵng", "từ xa", "remote")
    )
    if asks_jobs and not has_location:
        missing.append("địa điểm làm việc")

    asks_roadmap = any(term in text for term in ("lộ trình", "roadmap", "kế hoạch học"))
    has_timeframe = bool(
        re.search(r"\b\d+\s*(?:ngày|tuần|tháng|giờ)\b", text)
        or any(term in text for term in ("mỗi ngày", "mỗi tuần", "toàn thời gian", "bán thời gian"))
    )
    if asks_roadmap and not has_timeframe:
        missing.append("thời gian học")

    asks_fit = any(
        term in text
        for term in ("đánh giá độ phù hợp", "phân tích hồ sơ", "tôi hợp", "phù hợp với tôi")
    )
    has_skills = any(
        term in text
        for term in ("biết ", "kỹ năng", "giỏi ", "thành thạo", "kinh nghiệm", "đã làm")
    )
    if asks_fit and not has_skills:
        missing.append("kỹ năng/kinh nghiệm hiện có")

    asks_direction = any(
        term in text for term in ("định hướng cho tôi", "nên theo hướng nào", "mục tiêu nghề")
    )
    has_goal = any(
        term in text
        for term in ("muốn ", "mục tiêu", "trở thành", "chuyển sang", "ứng tuyển")
    )
    if asks_direction and not has_goal:
        missing.append("mục tiêu nghề nghiệp")
    return tuple(missing)


def check_input_guardrail(user_query: str) -> tuple[str | None, str | None]:
    """Tra guardrail code va cau tra loi an toan; None neu duoc phep."""
    if SYSTEM_SECRET_RE.search(user_query) and any(
        term in user_query.casefold()
        for term in ("cho xem", "hiện", "tiết lộ", "đưa tôi", "show", "reveal", "in ra")
    ):
        return (
            "SECRET_DISCLOSURE",
            "Tôi không thể tiết lộ system prompt, chỉ dẫn nội bộ hoặc API key. "
            "Tôi vẫn có thể giải thích công khai cách OreoAI định tuyến và dùng tool.",
        )
    if contains_sensitive_data(user_query):
        return (
            "SENSITIVE_DATA",
            "Vui lòng xóa hoặc che API key, mật khẩu, số CCCD hay dữ liệu nhạy cảm "
            "trước khi tiếp tục. OreoAI không cần các thông tin này để tư vấn nghề.",
        )
    if USER_INJECTION_RE.search(user_query):
        return (
            "PROMPT_INJECTION",
            "Yêu cầu này cố gắng thay đổi hoặc vô hiệu hóa quy tắc an toàn nên tôi "
            "không thực hiện. Bạn có thể đặt lại câu hỏi định hướng nghề nghiệp trực tiếp.",
        )
    if FABRICATION_RE.search(user_query):
        return (
            "UNGROUNDED_DATA_REQUEST",
            "Tôi không thể bịa mức lương, tin tuyển dụng hoặc chứng chỉ. Nếu chưa "
            "có nguồn phù hợp, tôi sẽ nói rõ giới hạn và đề nghị bạn kiểm chứng.",
        )
    if DISCRIMINATION_RE.search(user_query):
        return (
            "DISCRIMINATION",
            "OreoAI không loại trừ hoặc xếp hạng ứng viên theo giới tính, dân tộc, "
            "tôn giáo, khuyết tật hay thuộc tính được bảo vệ. Hãy dùng tiêu chí liên "
            "quan trực tiếp đến công việc như kỹ năng và kinh nghiệm.",
        )
    return None, None


def decide_route(user_query: str, requested_mode: str = "auto") -> RouteDecision:
    """Guardrail -> clarification -> Agentic Fit -> hybrid route."""
    fit = evaluate_agentic_fit(user_query)
    guardrail_code, _ = check_input_guardrail(user_query)
    if guardrail_code:
        return RouteDecision(
            route="guardrail",
            reason="Đầu vào vi phạm guardrail cấp ứng dụng.",
            fit=fit,
            guardrail_code=guardrail_code,
        )
    missing = detect_missing_information(user_query)
    if missing:
        return RouteDecision(
            route="clarification",
            reason="Thiếu thông tin thiết yếu; không được tự đoán tham số.",
            fit=fit,
            missing_fields=missing,
        )
    if requested_mode in {"chatbot", "react"}:
        return RouteDecision(
            route=requested_mode,
            reason=f"Chế độ {requested_mode} do người dùng chọn để so sánh Lab.",
            fit=fit,
        )
    route = (
        "react"
        if fit.recommendation == "react"
        or (fit.recommendation == "hybrid" and fit.external_data > 0)
        else "chatbot"
    )
    return RouteDecision(
        route=route,
        reason=(
            "Cần dữ liệu ngoài/cập nhật và quan sát kết quả tool."
            if route == "react"
            else "LLM đủ khả năng trả lời từ kiến thức ổn định; không cần tool."
        ),
        fit=fit,
    )


def run_baseline_chatbot(
    user_query: str,
    provider: BaseLLMProvider,
    *,
    verbose: bool = True,
    request_id: str | None = None,
    route: str = "chatbot",
) -> AgentResult:
    """Gọi LLM đúng một lần và tuyệt đối không cấp tool cho baseline."""
    started = perf_counter()
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    current_request_id = request_id or str(uuid4())
    result = AgentResult(
        answer=response,
        trace=[response],
        iterations=1,
        route=route,
        request_id=current_request_id,
        trace_log=[
            _trace_event(
                request_id=current_request_id,
                route=route,
                selected_tool=None,
                tool_input=None,
                tool_status="not_called",
                latency_ms=round((perf_counter() - started) * 1000),
                retry_count=0,
                error_code=None,
                final_status="completed",
            )
        ],
    )
    if verbose:
        print(f"\n💬 [CHATBOT BASELINE] {user_query}")
        print(f"🤖 Final Answer: {response}")
    return result


def parse_action(model_output: str) -> tuple[str, list[Any]]:
    """Parse ``Action: tool[arg1, arg2]`` bằng AST, không dùng eval."""
    match = ACTION_RE.search(model_output)
    if not match:
        raise ValueError("Không tìm thấy Action đúng định dạng tool[arg1, arg2].")
    tool_name, raw_args = match.groups()
    try:
        parsed = ast.literal_eval(f"[{raw_args}]")
    except (SyntaxError, ValueError) as exc:
        raise ValueError("Tham số Action sai cú pháp; hãy dùng chuỗi có dấu nháy.") from exc
    if not isinstance(parsed, list) or any(
        not isinstance(value, (str, int, float, bool, type(None))) for value in parsed
    ):
        raise ValueError("Action chỉ chấp nhận các tham số vô hướng an toàn.")
    return tool_name, parsed


def _tool_failure(
    code: str,
    message: str,
    *,
    started: float,
    retry_count: int = 0,
) -> ToolExecution:
    return ToolExecution(
        observation=f"LỖI: {message}\nerror_code={code}",
        status="error",
        latency_ms=round((perf_counter() - started) * 1000),
        retry_count=retry_count,
        error_code=code,
    )


def execute_tool_detailed(
    tool_name: str,
    args: list[Any],
    *,
    max_retries: int = 1,
) -> ToolExecution:
    """Xac thuc schema, chay read-only tool, retry gioi han va tra metadata."""
    started = perf_counter()
    tool = AVAILABLE_TOOLS.get(tool_name)
    if tool is None:
        valid = ", ".join(sorted(AVAILABLE_TOOLS))
        return _tool_failure(
            "TOOL_NOT_FOUND",
            f"Tool '{tool_name}' không tồn tại. Tool hợp lệ: {valid}.",
            started=started,
        )
    if tool_name not in TOOL_SPECS:
        return _tool_failure(
            "TOOL_SPEC_MISSING",
            f"Tool '{tool_name}' chưa có specification nên bị từ chối.",
            started=started,
        )
    try:
        inspect.signature(tool).bind(*args)
    except TypeError as exc:
        return _tool_failure(
            "INVALID_TOOL_INPUT",
            f"Sai tham số cho tool '{tool_name}': {exc}.",
            started=started,
        )
    if any(isinstance(value, str) and contains_sensitive_data(value) for value in args):
        return _tool_failure(
            "SENSITIVE_TOOL_INPUT",
            "Tool input có dữ liệu nhạy cảm và đã bị chặn.",
            started=started,
        )

    retry_count = 0
    while retry_count <= max_retries:
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(tool, *args)
        try:
            value = future.result(timeout=TIMEOUT_SECONDS)
            if not isinstance(value, str):
                return _tool_failure(
                    "SCHEMA_MISMATCH",
                    f"Tool '{tool_name}' trả kiểu {type(value).__name__}, cần chuỗi.",
                    started=started,
                    retry_count=retry_count,
                )
            value = value.strip()
            if not value:
                return _tool_failure(
                    "EMPTY_RESULT",
                    f"Tool '{tool_name}' không trả dữ liệu.",
                    started=started,
                    retry_count=retry_count,
                )
            if value.startswith("LOI:") or value.startswith("LỖI:"):
                code_match = re.search(r"error_code=([A-Z0-9_]+)", value)
                return ToolExecution(
                    observation=value,
                    status="error",
                    latency_ms=round((perf_counter() - started) * 1000),
                    retry_count=retry_count,
                    error_code=code_match.group(1) if code_match else "TOOL_ERROR",
                )
            if TOOL_INJECTION_RE.search(value):
                return _tool_failure(
                    "UNSAFE_TOOL_OUTPUT",
                    "Tool output chứa chỉ dẫn có khả năng điều khiển Agent và đã bị loại bỏ.",
                    started=started,
                    retry_count=retry_count,
                )
            expected_source = TOOL_SPECS[tool_name].get("source")
            if expected_source and f'source="{expected_source}"' not in value:
                return _tool_failure(
                    "SCHEMA_MISMATCH",
                    f"Tool '{tool_name}' thiếu trường source bắt buộc.",
                    started=started,
                    retry_count=retry_count,
                )
            if len(value) > 20_000:
                return _tool_failure(
                    "SCHEMA_MISMATCH",
                    f"Tool '{tool_name}' trả output vượt giới hạn.",
                    started=started,
                    retry_count=retry_count,
                )
            return ToolExecution(
                observation=value,
                status="success",
                latency_ms=round((perf_counter() - started) * 1000),
                retry_count=retry_count,
            )
        except FutureTimeout:
            future.cancel()
            if retry_count >= max_retries:
                return _tool_failure(
                    "TOOL_TIMEOUT",
                    f"Tool '{tool_name}' vượt quá timeout {TIMEOUT_SECONDS} giây.",
                    started=started,
                    retry_count=retry_count,
                )
            retry_count += 1
        except Exception as exc:  # Tool loi khong duoc lam crash Agent.
            if retry_count >= max_retries:
                return _tool_failure(
                    "TOOL_UNAVAILABLE",
                    f"Tool '{tool_name}' gặp sự cố: {exc}.",
                    started=started,
                    retry_count=retry_count,
                )
            retry_count += 1
        finally:
            executor.shutdown(wait=False, cancel_futures=True)
    return _tool_failure(
        "TOOL_UNAVAILABLE",
        f"Tool '{tool_name}' không hoàn thành.",
        started=started,
        retry_count=retry_count,
    )


def execute_tool(tool_name: str, args: list[Any]) -> str:
    """API cu: tra observation string, implementation moi co structured metadata."""
    return execute_tool_detailed(tool_name, args).observation


def _build_agent_prompt(user_query: str, transcript: list[str]) -> str:
    history = "\n".join(transcript) if transcript else "(chưa có)"
    return (
        f"Question: {user_query}\n\n"
        f"Lịch sử ReAct do ứng dụng ghi nhận:\n{history}\n\n"
        "Hãy đưa ra đúng một Action tiếp theo hoặc Final Answer."
    )


def _observable_model_output(model_output: str) -> str:
    """An Thought khoi CLI; chi hien thi Action hoac Final Answer quan sat duoc."""
    visible: list[str] = []
    include = False
    for line in model_output.splitlines():
        if re.match(r"^\s*Thought\s*:", line, flags=re.IGNORECASE):
            include = False
            continue
        if re.match(r"^\s*(?:Action|Final Answer)\s*:", line, flags=re.IGNORECASE):
            include = True
        if include:
            visible.append(line)
    return "\n".join(visible).strip() or "[Bước suy luận nội bộ đã được ẩn]"


def run_react_agent(
    user_query: str,
    provider: BaseLLMProvider,
    *,
    verbose: bool = True,
    request_id: str | None = None,
    route: str = "react",
) -> AgentResult:
    """Chạy ReAct V2: parse, execute, append Observation và dừng an toàn."""
    transcript: list[str] = []
    trace_log: list[dict[str, Any]] = []
    seen_actions: set[tuple[str, tuple[Any, ...]]] = set()
    tool_calls = 0
    current_request_id = request_id or str(uuid4())

    if verbose:
        print(f"\n🧠 [REACT AGENT] {user_query}")

    for step in range(1, MAX_ITERATIONS + 1):
        prompt = _build_agent_prompt(user_query, transcript)
        output = provider.generate(prompt, system_prompt=REACT_SYSTEM_PROMPT).strip()
        transcript.append(output)
        if verbose:
            print(
                f"\n--- Step {step}/{MAX_ITERATIONS} ---\n"
                f"{_observable_model_output(output)}"
            )

        final_match = FINAL_RE.search(output)
        if final_match:
            answer = final_match.group(1).strip()
            trace_log.append(
                _trace_event(
                    request_id=current_request_id,
                    route=route,
                    selected_tool=None,
                    tool_input=None,
                    tool_status="not_called",
                    latency_ms=0,
                    retry_count=0,
                    error_code=None,
                    final_status="completed",
                )
            )
            return AgentResult(
                answer=answer,
                trace=transcript,
                tool_calls=tool_calls,
                iterations=step,
                route=route,
                request_id=current_request_id,
                trace_log=trace_log,
            )

        try:
            tool_name, args = parse_action(output)
            action_key = (tool_name, tuple(args))
            if action_key in seen_actions:
                observation = (
                    "LỖI: Action bị lặp lại với cùng tham số. "
                    "Hãy trả lời fallback hoặc chọn hành động khác."
                )
                trace_log.append(
                    _trace_event(
                        request_id=current_request_id,
                        route=route,
                        selected_tool=tool_name,
                        tool_input=args,
                        tool_status="blocked",
                        latency_ms=0,
                        retry_count=0,
                        error_code="REPEATED_ACTION",
                        final_status="guardrail_blocked",
                    )
                )
            else:
                seen_actions.add(action_key)
                execution = execute_tool_detailed(tool_name, args)
                observation = execution.observation
                tool_calls += 1
                trace_log.append(
                    _trace_event(
                        request_id=current_request_id,
                        route=route,
                        selected_tool=tool_name,
                        tool_input=args,
                        tool_status=execution.status,
                        latency_ms=execution.latency_ms,
                        retry_count=execution.retry_count,
                        error_code=execution.error_code,
                        final_status=(
                            "tool_completed"
                            if execution.status == "success"
                            else "tool_failed"
                        ),
                    )
                )
        except ValueError as exc:
            observation = f"LỖI: {exc}"
            trace_log.append(
                _trace_event(
                    request_id=current_request_id,
                    route=route,
                    selected_tool=None,
                    tool_input=None,
                    tool_status="blocked",
                    latency_ms=0,
                    retry_count=0,
                    error_code="MALFORMED_ACTION",
                    final_status="guardrail_blocked",
                )
            )

        observation_line = f"Observation: {observation}"
        transcript.append(observation_line)
        if verbose:
            print(observation_line)

    answer = (
        f"Xin lỗi, tôi chưa thể hoàn thành yêu cầu an toàn sau "
        f"{MAX_ITERATIONS} bước. Vui lòng kiểm tra lại yêu cầu hoặc tham số."
    )
    if verbose:
        print(f"🛡️ GUARDRAIL: {answer}")
    trace_log.append(
        _trace_event(
            request_id=current_request_id,
            route=route,
            selected_tool=None,
            tool_input=None,
            tool_status="not_called",
            latency_ms=0,
            retry_count=0,
            error_code="MAX_ITERATIONS",
            final_status="guardrail_stopped",
        )
    )
    return AgentResult(
        answer=answer,
        trace=transcript,
        tool_calls=tool_calls,
        iterations=MAX_ITERATIONS,
        guardrail_triggered=True,
        route=route,
        request_id=current_request_id,
        trace_log=trace_log,
    )


def run_hybrid_agent(
    user_query: str,
    provider: BaseLLMProvider,
    *,
    requested_mode: str = "auto",
    verbose: bool = False,
) -> AgentResult:
    """Entry point Hybrid: guardrail/clarification/chatbot/react co cung trace."""
    current_request_id = str(uuid4())
    decision = decide_route(user_query, requested_mode)
    fit_payload = decision.fit.as_dict()
    guardrail_code, guardrail_answer = check_input_guardrail(user_query)

    if decision.route == "guardrail":
        return AgentResult(
            answer=guardrail_answer or "Yêu cầu đã bị guardrail chặn.",
            iterations=0,
            guardrail_triggered=True,
            route="guardrail",
            request_id=current_request_id,
            trace_log=[
                _trace_event(
                    request_id=current_request_id,
                    route="guardrail",
                    selected_tool=None,
                    tool_input=None,
                    tool_status="blocked",
                    latency_ms=0,
                    retry_count=0,
                    error_code=guardrail_code,
                    final_status="guardrail_blocked",
                )
            ],
            agentic_fit=fit_payload,
        )

    if decision.route == "clarification":
        questions = {
            "địa điểm làm việc": "Bạn muốn làm việc ở tỉnh/thành phố nào hay làm từ xa?",
            "thời gian học": "Bạn có thể học trong bao lâu và dành bao nhiêu giờ mỗi tuần?",
            "kỹ năng/kinh nghiệm hiện có": "Bạn đang có kỹ năng, môn học mạnh hoặc kinh nghiệm nào liên quan?",
            "mục tiêu nghề nghiệp": "Mục tiêu nghề nghiệp cụ thể bạn muốn đạt được là gì?",
        }
        answer = (
            "Tôi cần làm rõ vài thông tin trước khi tư vấn hoặc gọi tool:\n- "
            + "\n- ".join(questions[field] for field in decision.missing_fields)
            + "\nTôi sẽ không tự đoán các thông tin này."
        )
        return AgentResult(
            answer=answer,
            iterations=0,
            route="clarification",
            request_id=current_request_id,
            trace_log=[
                _trace_event(
                    request_id=current_request_id,
                    route="clarification",
                    selected_tool=None,
                    tool_input=None,
                    tool_status="not_called",
                    latency_ms=0,
                    retry_count=0,
                    error_code="MISSING_INFORMATION",
                    final_status="needs_clarification",
                )
            ],
            agentic_fit=fit_payload,
        )

    if decision.route == "react":
        result = run_react_agent(
            user_query,
            provider,
            verbose=verbose,
            request_id=current_request_id,
            route="react",
        )
    else:
        result = run_baseline_chatbot(
            user_query,
            provider,
            verbose=verbose,
            request_id=current_request_id,
            route="chatbot",
        )
    result.agentic_fit = fit_payload
    return result


def parse_react_response(
    text: str,
) -> tuple[str | None, str | None, list[Any] | None, str | None]:
    """Compatibility wrapper cho API parser cũ từ origin/main."""
    thought_match = re.search(
        r"^\s*Thought\s*:\s*(.*)$",
        text,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    thought = thought_match.group(1).strip() if thought_match else None
    final_match = FINAL_RE.search(text)
    final_answer = final_match.group(1).strip() if final_match else None
    action_name: str | None = None
    action_args: list[Any] | None = None
    try:
        action_name, action_args = parse_action(text)
    except ValueError:
        pass
    if not final_answer and not action_name and thought:
        final_answer = text.strip()
    return thought, action_name, action_args, final_answer


def run_all_tests(provider: BaseLLMProvider) -> list[dict[str, Any]]:
    """Compatibility wrapper: chạy 17 case cũ qua Baseline và ReAct."""
    results: list[dict[str, Any]] = []
    for case in load_test_cases():
        baseline = run_baseline_chatbot(case["question"], provider, verbose=False)
        react = run_react_agent(case["question"], provider, verbose=False)
        results.append(
            {
                "id": case["id"],
                "question": case["question"],
                "category": case["category"],
                "chatbot": baseline.answer,
                "agent": react.answer,
            }
        )
    return results


def generate_comparison_report(results: list[dict[str, Any]]) -> None:
    """Compatibility wrapper cho báo cáo console của Core App cũ."""
    print("=" * 80)
    print("COMPARISON REPORT: CHATBOT BASELINE vs REACT AGENT")
    print("=" * 80)
    for row in results:
        print(f"\n--- Test #{row['id']}: [{row['category']}] ---")
        print(f"Q: {row['question']}")
        print(f"Chatbot: {str(row['chatbot'])[:120]}...")
        print(f"Agent:   {str(row['agent'])[:120]}...")
    print(f"\nAgent tools available: {list(AVAILABLE_TOOLS)}")
    print(f"Guardrail: max {MAX_ITERATIONS} iterations per query.")


def main() -> None:
    """Chạy baseline, ReAct hoặc cả hai trên toàn bộ bộ đề."""
    parser = argparse.ArgumentParser(description="OreoAI: Chatbot baseline vs ReAct Agent")
    parser.add_argument(
        "--web",
        action="store_true",
        help="Khởi động giao diện web OreoAI.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Cổng cho giao diện web (mặc định: 8000).",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Không tự động mở trình duyệt khi chạy giao diện.",
    )
    parser.add_argument(
        "--mode",
        choices=("baseline", "react", "all"),
        default="all",
        help="Chọn hệ thống cần chạy (mặc định: all).",
    )
    args = parser.parse_args()

    if args.web:
        from web_server import run_web_app

        run_web_app(port=args.port, open_browser=not args.no_browser)
        return

    print("=" * 64)
    print("OREOAI - CHATBOT BASELINE VS REACT AGENT")
    print("=" * 64)
    provider = get_llm_provider()
    model = getattr(provider, "model_name", "offline-deterministic")
    print(f"Provider: {provider.__class__.__name__} ({model})")

    cases = load_test_cases()
    print(f"Đã tải {len(cases)} test cases.")
    for case in cases:
        print(f"\n{'=' * 64}\nTEST #{case['id']}: {case['category']}")
        if args.mode in ("baseline", "all"):
            run_baseline_chatbot(case["question"], provider)
        if args.mode in ("react", "all"):
            run_react_agent(case["question"], provider)


if __name__ == "__main__":
    main()
