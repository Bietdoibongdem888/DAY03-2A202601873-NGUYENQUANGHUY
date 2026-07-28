"""Máy chủ web nội bộ cho giao diện OreoAI."""

from __future__ import annotations

import json
import mimetypes
import re
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from app import AgentResult, decide_route, load_test_cases, run_hybrid_agent
from evaluator import run_acceptance_suite
from providers import BaseLLMProvider, get_llm_provider

ROOT_DIR = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT_DIR / "web"
MAX_BODY_BYTES = 65_536
MAX_QUESTION_LENGTH = 2_000
ALLOWED_MODES = {"auto", "chatbot", "react"}
REACT_KEYWORDS = (
    "tuyển dụng",
    "thực tập",
    "mức lương",
    "lương",
    "vị trí",
    "thị trường",
    "việc làm",
    "đang có",
    "triển vọng",
)


def choose_mode(question: str, requested_mode: str) -> str:
    """API tương thích cũ; Auto nay dùng Agentic Fit thay vì chỉ từ khóa."""
    route = decide_route(question, requested_mode).route
    return route if route in {"chatbot", "react"} else "chatbot"


def parse_trace(raw_trace: list[str], mode: str) -> list[dict[str, str]]:
    """Parser tương thích; tuyệt đối không trả Thought/Final nội bộ ra UI."""
    if mode != "react":
        return []

    names = {"action": "action", "observation": "observation"}
    marker = re.compile(
        r"^\s*(Thought|Action|Observation|Final Answer)\s*:\s*(.*)$",
        flags=re.IGNORECASE,
    )
    steps: list[dict[str, str]] = []

    for chunk in raw_trace:
        current_type: str | None = None
        current_lines: list[str] = []

        def flush() -> None:
            if current_type and current_lines:
                text = "\n".join(current_lines).strip()
                if text:
                    steps.append({"type": current_type, "text": text})

        for line in chunk.splitlines():
            match = marker.match(line)
            if match:
                flush()
                current_type = names.get(match.group(1).casefold())
                current_lines = [match.group(2)] if current_type else []
            elif current_type:
                current_lines.append(line)
        flush()
    return steps


def observable_trace(trace_log: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Đổi structured trace thành Action/Observation an toàn cho giao diện."""
    steps: list[dict[str, str]] = []
    for event in trace_log:
        tool_name = event.get("selected_tool")
        if tool_name:
            args = (event.get("tool_input") or {}).get("args", [])
            steps.append({"type": "action", "text": f"{tool_name}({args})"})
            status = event.get("tool_status", "unknown")
            detail = (
                f"status={status} · latency={event.get('latency_ms', 0)}ms"
                f" · retry={event.get('retry_count', 0)}"
            )
            if event.get("error_code"):
                detail += f" · error={event['error_code']}"
            steps.append({"type": "observation", "text": detail})
        elif event.get("final_status") in {
            "guardrail_blocked",
            "needs_clarification",
            "guardrail_stopped",
        }:
            steps.append(
                {
                    "type": "observation",
                    "text": (
                        f"route={event.get('route')} · status={event.get('final_status')}"
                        f" · error={event.get('error_code') or 'none'}"
                    ),
                }
            )
    return steps


def run_chat(
    question: str,
    requested_mode: str,
    provider: BaseLLMProvider,
) -> dict[str, Any]:
    """Thực thi một lượt chat bằng engine thật của dự án."""
    result: AgentResult = run_hybrid_agent(
        question,
        provider,
        requested_mode=requested_mode,
        verbose=False,
    )
    return {
        "answer": result.answer,
        "mode": result.route,
        "route": result.route,
        "trace": observable_trace(result.trace_log),
        "trace_log": result.trace_log,
        "request_id": result.request_id,
        "agentic_fit": result.agentic_fit,
        "tool_calls": result.tool_calls,
        "iterations": result.iterations,
        "guardrail_triggered": result.guardrail_triggered,
    }


class OreoAIHandler(BaseHTTPRequestHandler):
    """Phục vụ giao diện và API JSON trên cùng một cổng."""

    provider: BaseLLMProvider
    server_version = "OreoAI/1.0"

    def _send_json(
        self,
        payload: dict[str, Any],
        status: HTTPStatus = HTTPStatus.OK,
    ) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path) -> None:
        if not path.is_file() or WEB_DIR.resolve() not in path.resolve().parents:
            self.send_error(HTTPStatus.NOT_FOUND.value)
            return
        body = path.read_bytes()
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if path.suffix in {".html", ".css", ".js"}:
            content_type = f"{content_type}; charset=utf-8"
        self.send_response(HTTPStatus.OK.value)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        route = self.path.split("?", 1)[0]
        if route == "/api/health":
            self._send_json({"status": "ok", "app": "OreoAI"})
            return
        if route == "/api/test-cases":
            self._send_json(
                {
                    "cases": load_test_cases(include_extended=True),
                    "source": "mock deterministic",
                }
            )
            return
        routes = {
            "/": WEB_DIR / "index.html",
            "/index.html": WEB_DIR / "index.html",
            "/styles.css": WEB_DIR / "styles.css",
            "/app.js": WEB_DIR / "app.js",
            "/og.png": WEB_DIR / "og.png",
        }
        path = routes.get(route)
        if path is None:
            self.send_error(HTTPStatus.NOT_FOUND.value)
            return
        self._send_file(path)

    def do_POST(self) -> None:  # noqa: N802
        route = self.path.split("?", 1)[0]
        if route == "/api/test-suite":
            self._send_json(run_acceptance_suite())
            return
        if route != "/api/chat":
            self.send_error(HTTPStatus.NOT_FOUND.value)
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json({"error": "Content-Length không hợp lệ."}, HTTPStatus.BAD_REQUEST)
            return
        if content_length <= 0 or content_length > MAX_BODY_BYTES:
            self._send_json({"error": "Nội dung yêu cầu không hợp lệ."}, HTTPStatus.BAD_REQUEST)
            return
        try:
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json({"error": "JSON không hợp lệ."}, HTTPStatus.BAD_REQUEST)
            return

        question = payload.get("question", "")
        mode = payload.get("mode", "auto")
        if not isinstance(question, str) or not question.strip():
            self._send_json({"error": "Vui lòng nhập câu hỏi."}, HTTPStatus.BAD_REQUEST)
            return
        question = question.strip()
        if len(question) > MAX_QUESTION_LENGTH:
            self._send_json({"error": "Câu hỏi quá dài."}, HTTPStatus.BAD_REQUEST)
            return
        if mode not in ALLOWED_MODES:
            self._send_json({"error": "Chế độ không hợp lệ."}, HTTPStatus.BAD_REQUEST)
            return

        try:
            self._send_json(run_chat(question, mode, self.provider))
        except Exception:
            self._send_json(
                {"error": "OreoAI chưa thể xử lý yêu cầu. Vui lòng thử lại."},
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    def log_message(self, format: str, *args: Any) -> None:
        """Giữ terminal gọn khi dùng giao diện."""


def create_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    provider: BaseLLMProvider | None = None,
) -> ThreadingHTTPServer:
    """Tạo server để chạy thật hoặc kiểm thử bằng cổng ngẫu nhiên."""
    handler = type(
        "ConfiguredOreoAIHandler",
        (OreoAIHandler,),
        {"provider": provider or get_llm_provider()},
    )
    return ThreadingHTTPServer((host, port), handler)


def run_web_app(port: int = 8000, *, open_browser: bool = True) -> None:
    """Chạy UI và Agent trong một ứng dụng."""
    server = create_server(port=port)
    url = f"http://127.0.0.1:{server.server_address[1]}"
    print("=" * 64)
    print("OREOAI WEB APP")
    print("=" * 64)
    print(f"App đang chạy tại: {url}")
    print("Nhấn Ctrl+C để dừng.")
    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng OreoAI.")
    finally:
        server.server_close()
