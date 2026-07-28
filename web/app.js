const state = { mode: "auto", busy: false };
const labels = { auto: "Tự động", chatbot: "Chatbot", react: "ReAct Agent" };
const messages = document.querySelector("#messages");
const traceBody = document.querySelector("#trace-body");
const form = document.querySelector("#chat-form");
const questionInput = document.querySelector("#career-question");
const sendButton = document.querySelector("#send-button");
const modeLabel = document.querySelector("#mode-label");
const status = document.querySelector("#system-status");
const testDialog = document.querySelector("#test-dialog");
const testList = document.querySelector("#test-list");
const testResult = document.querySelector("#test-result");
const runTestSuite = document.querySelector("#run-test-suite");

function createMessage(role, text, note = "") {
  const article = document.createElement("article");
  article.className = `message ${role}`;
  const avatar = document.createElement("span");
  avatar.className = "avatar";
  avatar.setAttribute("aria-hidden", "true");
  avatar.textContent = role === "assistant" ? "O" : "B";
  const content = document.createElement("div");
  const author = document.createElement("small");
  author.textContent = role === "assistant" ? "OREOAI" : "BẠN";
  const paragraph = document.createElement("p");
  paragraph.textContent = text;
  content.append(author, paragraph);
  if (note) {
    const evidence = document.createElement("span");
    evidence.className = "evidence";
    evidence.textContent = note;
    content.append(evidence);
  }
  article.append(avatar, content);
  messages.append(article);
  messages.scrollTo({ top: messages.scrollHeight, behavior: "smooth" });
  return article;
}

function setBusy(busy) {
  state.busy = busy;
  sendButton.disabled = busy;
  questionInput.disabled = busy;
  status.classList.toggle("working", busy);
  status.lastChild.textContent = busy ? " OreoAI đang suy luận" : " Hệ thống sẵn sàng";
}

function renderTrace(steps, meta) {
  traceBody.replaceChildren();
  if (!steps.length) {
    const empty = document.createElement("div");
    empty.className = "trace-empty compact";
    const title = document.createElement("h3");
    title.textContent = "Chatbot path";
    const text = document.createElement("p");
    text.textContent = "Câu hỏi được xử lý trực tiếp, không cần gọi công cụ.";
    empty.append(title, text);
    traceBody.append(empty);
    return;
  }
  const list = document.createElement("ol");
  list.className = "trace-list";
  steps.forEach((step, index) => {
    const item = document.createElement("li");
    item.className = step.type;
    const number = document.createElement("span");
    number.textContent = String(index + 1);
    const content = document.createElement("div");
    const type = document.createElement("small");
    type.textContent = step.type;
    const text = document.createElement("p");
    text.textContent = step.text;
    content.append(type, text);
    item.append(number, content);
    list.append(item);
  });
  traceBody.append(list);
  const summary = document.createElement("div");
  summary.className = "trace-summary";
  summary.textContent = `${meta.iterations} vòng · ${meta.tool_calls} tool call${meta.guardrail_triggered ? " · Guardrail đã kích hoạt" : ""}`;
  traceBody.append(summary);
}

async function submitQuestion(rawQuestion) {
  const question = rawQuestion.trim();
  if (!question || state.busy) return;
  createMessage("user", question);
  questionInput.value = "";
  setBusy(true);
  const loading = createMessage("assistant", "Đang phân tích câu hỏi và kiểm tra dữ liệu…", "Đang xử lý");
  loading.classList.add("loading");
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, mode: state.mode }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Không thể xử lý yêu cầu.");
    loading.remove();
    const note = data.mode === "react"
      ? `ReAct · ${data.tool_calls} tool call · ${data.iterations} vòng · mock data`
      : data.mode === "clarification"
        ? "Clarification · chưa gọi tool"
        : data.mode === "guardrail"
          ? "Guardrail · yêu cầu đã được xử lý an toàn"
          : "Chatbot · không cần dữ liệu động";
    createMessage("assistant", data.answer, note);
    renderTrace(data.trace, data);
  } catch (error) {
    loading.remove();
    createMessage("assistant", `Xin lỗi, ứng dụng gặp lỗi: ${error.message}`, "Safe fallback");
  } finally {
    setBusy(false);
    questionInput.focus();
  }
}

document.querySelectorAll("[data-mode]").forEach((button) => {
  button.addEventListener("click", () => {
    state.mode = button.dataset.mode;
    document.querySelectorAll("[data-mode]").forEach((item) => {
      item.classList.toggle("active", item === button);
    });
    modeLabel.textContent = labels[state.mode];
  });
});
document.querySelectorAll("[data-question]").forEach((button) => {
  button.addEventListener("click", () => submitQuestion(button.dataset.question));
});
form.addEventListener("submit", (event) => {
  event.preventDefault();
  submitQuestion(questionInput.value);
});
questionInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

function renderTestCases(cases) {
  testList.replaceChildren();
  cases.forEach((testCase) => {
    const article = document.createElement("article");
    article.className = "test-case";
    article.dataset.caseId = String(testCase.id);
    const meta = document.createElement("small");
    meta.textContent = `#${String(testCase.id).padStart(2, "0")} · ${testCase.category}`;
    const question = document.createElement("p");
    question.textContent = testCase.question;
    const expected = document.createElement("details");
    const summary = document.createElement("summary");
    summary.textContent = "Expected behavior";
    const behavior = document.createElement("p");
    behavior.textContent = testCase.expected_behavior;
    expected.append(summary, behavior);
    const useCase = document.createElement("button");
    useCase.type = "button";
    useCase.textContent = "Dùng câu này trong chat ↗";
    useCase.addEventListener("click", () => {
      testDialog.close();
      submitQuestion(testCase.question);
    });
    const badges = document.createElement("div");
    badges.className = "test-badges";
    article.append(meta, question, expected, useCase, badges);
    testList.append(article);
  });
}

async function openTestSuite() {
  testDialog.showModal();
  if (testList.childElementCount) return;
  testList.textContent = "Đang tải 35 test cases…";
  try {
    const response = await fetch("/api/test-cases");
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Không tải được test cases.");
    renderTestCases(data.cases);
  } catch (error) {
    testList.textContent = error.message;
  }
}

async function executeTestSuite() {
  runTestSuite.disabled = true;
  runTestSuite.textContent = "Đang chạy 52 checks…";
  testResult.className = "test-result";
  testResult.textContent = "Đang nghiệm thu";
  try {
    const response = await fetch("/api/test-suite", { method: "POST" });
    const report = await response.json();
    if (!response.ok) throw new Error(report.error || "Không chạy được test suite.");
    testResult.textContent = `${report.passed}/${report.total} · ${report.score}/100`;
    testResult.classList.toggle("passed", report.all_passed);
    report.cases.forEach((row) => {
      const article = testList.querySelector(`[data-case-id="${row.id}"]`);
      if (!article) return;
      const badges = article.querySelector(".test-badges");
      badges.replaceChildren();
      if (row.test_type !== "behavioral") {
        const check = document.createElement("span");
        check.className = row.pass ? "pass" : "fail";
        check.textContent = `${row.test_type} ${row.pass ? "PASS" : "FAIL"}`;
        badges.append(check);
        return;
      }
      const baseline = document.createElement("span");
      baseline.className = row.baseline_pass ? "pass" : "fail";
      baseline.textContent = `Baseline ${row.baseline_pass ? "PASS" : "FAIL"}`;
      const react = document.createElement("span");
      react.className = row.react_pass ? "pass" : "fail";
      react.textContent = `ReAct ${row.react_pass ? "PASS" : "FAIL"} · ${row.tool_calls} tool`;
      badges.append(baseline, react);
    });
  } catch (error) {
    testResult.textContent = error.message;
  } finally {
    runTestSuite.disabled = false;
    runTestSuite.textContent = "Chạy lại toàn bộ";
  }
}

document.querySelector("#open-test-suite").addEventListener("click", openTestSuite);
document.querySelector("#close-test-suite").addEventListener("click", () => testDialog.close());
runTestSuite.addEventListener("click", executeTestSuite);
