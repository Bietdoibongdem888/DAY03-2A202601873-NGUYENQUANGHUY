"""
Web server for the Career Guidance AI demo.

Flask API + a browser UI for comparing the baseline chatbot with the ReAct agent.
"""

import csv
import io
import os
import re
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS

from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT
from providers import get_llm_provider
from tools import AVAILABLE_TOOLS

load_dotenv()

app = Flask(__name__)
CORS(app)
provider = get_llm_provider()


def parse_react_response(text: str):
    """Parse Thought, Action, and Final Answer blocks from a ReAct response."""
    thought = None
    action_name = None
    action_args = None
    final_answer = None
    lines = text.strip().split("\n")

    for i, line in enumerate(lines):
        line = line.strip()
        if line.lower().startswith("thought:"):
            thought = line.split(":", 1)[1].strip()
        elif line.lower().startswith("action:"):
            action = line.split(":", 1)[1].strip()
            match = re.match(r"(\w+)\s*[\[\(](.+)[\]\)]", action)
            if match:
                action_name = match.group(1)
                raw_args = match.group(2)
                try:
                    reader = csv.reader(io.StringIO(raw_args), quotechar="'", skipinitialspace=True)
                    args = next(reader)
                    if not args:
                        args = [arg.strip().strip("'\"") for arg in raw_args.split(",")]
                except Exception:
                    args = [arg.strip().strip("'\"") for arg in raw_args.split(",")]
                action_args = args
        elif line.lower().startswith("final answer:"):
            final_answer = line.split(":", 1)[1].strip()
            if i + 1 < len(lines):
                final_answer += "\n" + "\n".join(lines[i + 1 :])
            break

    if not final_answer and not action_name and thought:
        final_answer = text.strip()

    return thought, action_name, action_args, final_answer


def execute_tool(name: str, args: list):
    """Execute a registered tool and return a displayable observation."""
    if name in AVAILABLE_TOOLS:
        try:
            return AVAILABLE_TOOLS[name](*(args or []))
        except Exception as e:
            return f"LOI: {str(e)}"
    return f"LOI: Khong tim thay tool '{name}'"


@app.route("/")
def index():
    return render_template_string(
        HTML_TEMPLATE,
        provider_name=provider.__class__.__name__.replace("Provider", "") or "Mock",
        model=getattr(provider, "model_name", "Mock Mode"),
        tools=list(AVAILABLE_TOOLS.keys()),
    )


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    query = str(data.get("query", "")).strip()
    mode = data.get("mode", "chatbot")

    if not query:
        return jsonify({"error": "Question is required."}), 400

    try:
        max_iters = int(data.get("max_iterations", 5))
    except (TypeError, ValueError):
        max_iters = 5
    max_iters = max(1, min(max_iters, 15))

    if mode == "chatbot":
        try:
            response = provider.generate(query, system_prompt=CHATBOT_BASELINE_PROMPT)
            return jsonify({"type": "chatbot", "response": response})
        except Exception as e:
            return jsonify({"type": "chatbot", "error": str(e)}), 500

    steps = []
    messages = REACT_SYSTEM_PROMPT + f"\nUser question: {query}"
    final = None

    for step in range(1, max_iters + 1):
        try:
            response = provider.generate(messages, system_prompt="")
        except Exception as e:
            steps.append({"step": step, "error": str(e)})
            break

        thought, action_name, action_args, final_answer = parse_react_response(response)

        step_data = {
            "step": step,
            "thought": thought,
            "action": f"{action_name}{action_args}" if action_name else None,
        }

        if final_answer and action_name and action_args:
            deferred = final_answer
            observation = execute_tool(action_name, action_args)
            step_data["observation"] = observation
            messages += f"\nAssistant: {response}"
            messages += f"\nObservation: {observation}"
            messages += f"\nYou prepared this answer:\n{deferred}"
            messages += "\nJust output: Final Answer: [answer]\nNo more actions."
            steps.append(step_data)
            continue

        if final_answer:
            step_data["final"] = final_answer
            steps.append(step_data)
            final = final_answer
            break

        if action_name and action_args:
            observation = execute_tool(action_name, action_args)
            step_data["observation"] = observation
            messages += f"\nAssistant: {response}"
            messages += f"\nObservation: {observation}"
            messages += "\nWhat next?"
            steps.append(step_data)
        elif action_name:
            step_data["observation"] = f"Action '{action_name}' requires arguments."
            messages += f"\nAssistant: {response}"
            messages += f"\nObservation: {step_data['observation']}"
            steps.append(step_data)
        else:
            step_data["final"] = response.strip()
            steps.append(step_data)
            final = response.strip()
            break

    if not final:
        final = f"GUARDRAIL: Reached max {max_iters} iterations."
        steps.append({"step": max_iters, "final": final})

    return jsonify(
        {
            "type": "agent",
            "steps": steps,
            "final": final,
            "tools": list(AVAILABLE_TOOLS.keys()),
        }
    )


HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VinUni Career Guidance AI</title>
    <style>
        :root {
            color-scheme: dark;
            --bg: #08111f;
            --panel: rgba(15, 23, 42, 0.74);
            --panel-strong: rgba(15, 23, 42, 0.92);
            --card: rgba(255, 255, 255, 0.075);
            --card-strong: rgba(255, 255, 255, 0.11);
            --border: rgba(148, 163, 184, 0.22);
            --border-strong: rgba(148, 163, 184, 0.34);
            --text: #edf5ff;
            --muted: #96a4b8;
            --faint: #64748b;
            --accent: #38bdf8;
            --accent-2: #8b5cf6;
            --agent: #f97316;
            --success: #22c55e;
            --danger: #f43f5e;
            --shadow: 0 24px 80px rgba(0, 0, 0, 0.34);
            --radius-xl: 28px;
            --radius-lg: 20px;
            --radius-md: 14px;
        }

        * {
            box-sizing: border-box;
        }

        html,
        body {
            margin: 0;
            min-height: 100%;
        }

        body {
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background:
                radial-gradient(circle at top left, rgba(56, 189, 248, 0.24), transparent 34rem),
                radial-gradient(circle at 75% 20%, rgba(139, 92, 246, 0.22), transparent 32rem),
                linear-gradient(135deg, #070b16 0%, #08111f 42%, #111827 100%);
            color: var(--text);
            overflow: hidden;
        }

        button,
        input,
        textarea {
            font: inherit;
        }

        button {
            border: 0;
        }

        .shell {
            display: grid;
            grid-template-columns: 336px minmax(0, 1fr);
            gap: 18px;
            height: 100vh;
            padding: 18px;
        }

        .sidebar,
        .workspace {
            border: 1px solid var(--border);
            background: var(--panel);
            box-shadow: var(--shadow);
            backdrop-filter: blur(22px);
        }

        .sidebar {
            border-radius: var(--radius-xl);
            padding: 22px;
            overflow-y: auto;
        }

        .brand {
            display: flex;
            gap: 14px;
            align-items: center;
            margin-bottom: 22px;
        }

        .brand-mark {
            display: grid;
            width: 52px;
            height: 52px;
            place-items: center;
            border-radius: 18px;
            background: linear-gradient(135deg, var(--accent), var(--accent-2));
            color: #020617;
            font-size: 24px;
            font-weight: 900;
            box-shadow: 0 14px 40px rgba(56, 189, 248, 0.3);
        }

        .eyebrow {
            margin: 0 0 4px;
            color: var(--accent);
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }

        h1,
        h2,
        h3,
        p {
            margin-top: 0;
        }

        h1 {
            margin-bottom: 0;
            font-size: 22px;
            letter-spacing: -0.03em;
        }

        h2 {
            margin: 22px 0 10px;
            color: #cbd5e1;
            font-size: 12px;
            letter-spacing: 0.13em;
            text-transform: uppercase;
        }

        .status-card,
        .hint-card {
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            background: var(--card);
            padding: 16px;
        }

        .status-card {
            display: grid;
            gap: 12px;
        }

        .status-row {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            color: var(--muted);
            font-size: 13px;
        }

        .status-row strong {
            color: var(--text);
            font-weight: 700;
            text-align: right;
        }

        .mode-list {
            display: grid;
            gap: 10px;
        }

        .mode-card {
            width: 100%;
            border: 1px solid var(--border);
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.055);
            color: var(--text);
            cursor: pointer;
            padding: 14px;
            text-align: left;
            transition: border-color 0.18s ease, background 0.18s ease, transform 0.18s ease;
        }

        .mode-card:hover {
            transform: translateY(-1px);
            border-color: var(--border-strong);
            background: rgba(255, 255, 255, 0.085);
        }

        .mode-card.is-active {
            border-color: rgba(56, 189, 248, 0.8);
            background: linear-gradient(135deg, rgba(56, 189, 248, 0.18), rgba(139, 92, 246, 0.13));
            box-shadow: inset 0 0 0 1px rgba(56, 189, 248, 0.1);
        }

        .mode-title {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
            font-size: 14px;
            font-weight: 800;
        }

        .mode-title span:last-child {
            color: var(--accent);
            font-size: 12px;
            opacity: 0;
        }

        .mode-card.is-active .mode-title span:last-child {
            opacity: 1;
        }

        .mode-copy,
        .hint-card,
        .small-copy {
            color: var(--muted);
            font-size: 13px;
            line-height: 1.5;
        }

        .mode-copy {
            margin: 6px 0 0;
        }

        .slider-row {
            display: grid;
            grid-template-columns: 1fr 44px;
            gap: 12px;
            align-items: center;
        }

        input[type="range"] {
            width: 100%;
            accent-color: var(--accent);
        }

        .slider-value {
            display: grid;
            min-height: 34px;
            place-items: center;
            border-radius: 999px;
            background: rgba(56, 189, 248, 0.14);
            color: #7dd3fc;
            font-weight: 800;
        }

        .tool-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .tool-chip {
            border: 1px solid var(--border);
            border-radius: 999px;
            background: rgba(2, 6, 23, 0.36);
            color: #cbd5e1;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 11px;
            padding: 7px 10px;
        }

        .workspace {
            display: grid;
            grid-template-rows: auto 1fr auto;
            min-width: 0;
            border-radius: var(--radius-xl);
            overflow: hidden;
        }

        .topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            border-bottom: 1px solid var(--border);
            background: rgba(2, 6, 23, 0.22);
            padding: 18px 22px;
        }

        .topbar h2 {
            margin: 0 0 4px;
            color: var(--text);
            font-size: 18px;
            letter-spacing: -0.02em;
            text-transform: none;
        }

        .topbar p {
            margin: 0;
        }

        .ghost-button {
            border: 1px solid var(--border);
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.06);
            color: #dbeafe;
            cursor: pointer;
            font-weight: 750;
            padding: 10px 14px;
            transition: background 0.18s ease, border-color 0.18s ease;
            white-space: nowrap;
        }

        .ghost-button:hover {
            border-color: var(--border-strong);
            background: rgba(255, 255, 255, 0.1);
        }

        .chat-area {
            min-height: 0;
            overflow-y: auto;
            padding: 22px;
            scroll-behavior: smooth;
        }

        .hero {
            position: relative;
            overflow: hidden;
            border: 1px solid var(--border);
            border-radius: var(--radius-xl);
            background:
                linear-gradient(135deg, rgba(56, 189, 248, 0.18), rgba(249, 115, 22, 0.11)),
                rgba(255, 255, 255, 0.055);
            padding: 26px;
        }

        .hero::after {
            position: absolute;
            right: -52px;
            top: -52px;
            width: 180px;
            height: 180px;
            border-radius: 999px;
            background: rgba(56, 189, 248, 0.15);
            content: "";
        }

        .hero h2 {
            position: relative;
            margin: 0 0 8px;
            color: var(--text);
            font-size: clamp(26px, 4vw, 42px);
            letter-spacing: -0.05em;
            line-height: 1.04;
            text-transform: none;
        }

        .hero p {
            position: relative;
            max-width: 760px;
            margin: 0;
            color: #cbd5e1;
            line-height: 1.65;
        }

        .message-list {
            display: grid;
            gap: 14px;
            margin-top: 18px;
        }

        .message {
            max-width: min(860px, 92%);
            border: 1px solid var(--border);
            border-radius: 22px;
            background: rgba(255, 255, 255, 0.07);
            box-shadow: 0 16px 48px rgba(0, 0, 0, 0.18);
            padding: 16px;
            animation: rise 0.22s ease-out;
        }

        @keyframes rise {
            from {
                opacity: 0;
                transform: translateY(8px);
            }

            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message.user {
            justify-self: end;
            border-color: rgba(56, 189, 248, 0.35);
            background: linear-gradient(135deg, rgba(56, 189, 248, 0.92), rgba(139, 92, 246, 0.86));
            color: #020617;
        }

        .message.chatbot {
            justify-self: start;
        }

        .message.agent {
            justify-self: start;
            border-color: rgba(249, 115, 22, 0.28);
            background: linear-gradient(135deg, rgba(249, 115, 22, 0.13), rgba(255, 255, 255, 0.07));
        }

        .message.error {
            border-color: rgba(244, 63, 94, 0.45);
        }

        .message-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 10px;
        }

        .label {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            color: #cbd5e1;
            font-size: 12px;
            font-weight: 850;
            letter-spacing: 0.09em;
            text-transform: uppercase;
        }

        .user .label {
            color: rgba(2, 6, 23, 0.74);
        }

        .badge {
            border: 1px solid var(--border);
            border-radius: 999px;
            color: var(--muted);
            font-size: 11px;
            font-weight: 800;
            padding: 5px 8px;
            white-space: nowrap;
        }

        .message p,
        .answer {
            margin: 0;
            line-height: 1.68;
            white-space: normal;
        }

        .answer {
            color: #e5edf7;
        }

        .user p {
            color: #020617;
            font-weight: 650;
        }

        .trace {
            display: grid;
            gap: 10px;
            margin-top: 14px;
        }

        .trace-step {
            border: 1px solid var(--border);
            border-radius: 16px;
            background: rgba(2, 6, 23, 0.32);
            overflow: hidden;
        }

        .trace-step summary {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            cursor: pointer;
            list-style: none;
            padding: 12px 14px;
            color: #cbd5e1;
            font-size: 13px;
            font-weight: 800;
        }

        .trace-step summary::-webkit-details-marker {
            display: none;
        }

        .trace-type {
            color: var(--accent);
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 11px;
        }

        .trace-body {
            display: grid;
            gap: 9px;
            border-top: 1px solid var(--border);
            padding: 12px 14px 14px;
        }

        .trace-row {
            display: grid;
            gap: 5px;
        }

        .trace-row span {
            color: var(--faint);
            font-size: 11px;
            font-weight: 900;
            letter-spacing: 0.09em;
            text-transform: uppercase;
        }

        .trace-row p {
            margin: 0;
            color: #dbeafe;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 12px;
            line-height: 1.6;
        }

        .final-card {
            border: 1px solid rgba(34, 197, 94, 0.25);
            border-radius: 18px;
            background: rgba(34, 197, 94, 0.08);
            margin-top: 14px;
            padding: 14px;
        }

        .loader {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            color: var(--muted);
        }

        .dots {
            display: inline-flex;
            gap: 4px;
        }

        .dots span {
            width: 6px;
            height: 6px;
            border-radius: 999px;
            background: var(--accent);
            animation: pulse 1s infinite ease-in-out;
        }

        .dots span:nth-child(2) {
            animation-delay: 0.14s;
        }

        .dots span:nth-child(3) {
            animation-delay: 0.28s;
        }

        @keyframes pulse {
            0%,
            80%,
            100% {
                opacity: 0.25;
                transform: translateY(0);
            }

            40% {
                opacity: 1;
                transform: translateY(-3px);
            }
        }

        .composer {
            border-top: 1px solid var(--border);
            background: var(--panel-strong);
            padding: 16px 22px 20px;
        }

        .suggestions {
            display: flex;
            gap: 8px;
            margin-bottom: 12px;
            overflow-x: auto;
            padding-bottom: 2px;
        }

        .suggestion {
            border: 1px solid var(--border);
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.055);
            color: #dbeafe;
            cursor: pointer;
            flex: 0 0 auto;
            font-size: 12px;
            font-weight: 750;
            padding: 9px 12px;
        }

        .suggestion:hover {
            background: rgba(255, 255, 255, 0.1);
        }

        .input-shell {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 12px;
            align-items: end;
            border: 1px solid var(--border);
            border-radius: 22px;
            background: rgba(2, 6, 23, 0.45);
            padding: 10px;
        }

        textarea {
            width: 100%;
            max-height: 160px;
            min-height: 48px;
            resize: none;
            border: 0;
            outline: 0;
            background: transparent;
            color: var(--text);
            line-height: 1.5;
            padding: 12px 10px;
        }

        textarea::placeholder {
            color: #64748b;
        }

        .send-button {
            min-height: 48px;
            border-radius: 16px;
            background: linear-gradient(135deg, var(--accent), var(--accent-2));
            color: #020617;
            cursor: pointer;
            font-weight: 900;
            padding: 0 20px;
            transition: opacity 0.18s ease, transform 0.18s ease;
        }

        .send-button:hover:not(:disabled) {
            transform: translateY(-1px);
        }

        .send-button:disabled {
            cursor: wait;
            opacity: 0.58;
        }

        @media (max-width: 980px) {
            body {
                overflow: auto;
            }

            .shell {
                grid-template-columns: 1fr;
                height: auto;
                min-height: 100vh;
            }

            .sidebar {
                overflow: visible;
            }

            .workspace {
                min-height: 72vh;
            }

            .tool-grid {
                max-height: 96px;
                overflow: auto;
            }
        }

        @media (max-width: 640px) {
            .shell {
                padding: 10px;
            }

            .sidebar,
            .workspace {
                border-radius: 22px;
            }

            .topbar,
            .composer,
            .chat-area {
                padding-left: 14px;
                padding-right: 14px;
            }

            .topbar {
                align-items: flex-start;
                flex-direction: column;
            }

            .hero {
                padding: 20px;
            }

            .message {
                max-width: 100%;
            }

            .input-shell {
                grid-template-columns: 1fr;
            }

            .send-button {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="shell">
        <aside class="sidebar">
            <div class="brand">
                <div class="brand-mark">V</div>
                <div>
                    <p class="eyebrow">VinUni AI Lab</p>
                    <h1>Career Guidance AI</h1>
                </div>
            </div>

            <div class="status-card">
                <div class="status-row">
                    <span>Provider</span>
                    <strong>{{ provider_name }}</strong>
                </div>
                <div class="status-row">
                    <span>Model</span>
                    <strong>{{ model }}</strong>
                </div>
                <div class="status-row">
                    <span>UI</span>
                    <strong>Web demo</strong>
                </div>
            </div>

            <h2>Mode</h2>
            <div class="mode-list" role="group" aria-label="Response mode">
                <button class="mode-card is-active" type="button" data-mode="agent">
                    <div class="mode-title">
                        <span>ReAct Agent</span>
                        <span>Active</span>
                    </div>
                    <p class="mode-copy">Uses tool calls and shows each reasoning/action step.</p>
                </button>
                <button class="mode-card" type="button" data-mode="chatbot">
                    <div class="mode-title">
                        <span>Chatbot Baseline</span>
                        <span>Active</span>
                    </div>
                    <p class="mode-copy">Answers directly from the model without external tools.</p>
                </button>
                <button class="mode-card" type="button" data-mode="both">
                    <div class="mode-title">
                        <span>Compare Both</span>
                        <span>Active</span>
                    </div>
                    <p class="mode-copy">Runs both paths side-by-side in the conversation.</p>
                </button>
            </div>

            <h2>Guardrail</h2>
            <div class="slider-row">
                <input id="iterSlider" type="range" min="1" max="15" value="5">
                <span class="slider-value" id="iterVal">5</span>
            </div>
            <p class="small-copy">Maximum ReAct loops before the app stops the agent.</p>

            <h2>Tools</h2>
            <div class="tool-grid">
                {% for tool in tools %}
                <span class="tool-chip">{{ tool }}</span>
                {% endfor %}
            </div>

            <h2>Use case</h2>
            <div class="hint-card">
                Ask about career paths, skill gaps, courses, salary bands, and job-market signals. Use compare mode when you want to show why tools improve the answer.
            </div>
        </aside>

        <main class="workspace">
            <header class="topbar">
                <div>
                    <h2>Chat workspace</h2>
                    <p class="small-copy">Baseline vs tool-using agent, with trace visibility for demos and grading.</p>
                </div>
                <button class="ghost-button" type="button" id="clearButton">Clear chat</button>
            </header>

            <section class="chat-area" id="chatArea" aria-live="polite">
                <div class="hero">
                    <p class="eyebrow">Modernized interface</p>
                    <h2>Ask a career question and inspect how the agent works.</h2>
                    <p>
                        The agent path shows Thought, Action, Observation, and Final Answer steps.
                        The baseline path stays simple so you can compare output quality clearly.
                    </p>
                </div>
                <div class="message-list" id="messageList"></div>
            </section>

            <footer class="composer">
                <div class="suggestions" aria-label="Example prompts">
                    <button class="suggestion" type="button" data-example="Thị trường Data Science hiện nay ra sao?">Data Science market</button>
                    <button class="suggestion" type="button" data-example="Tôi biết Python và SQL, còn thiếu kỹ năng gì để làm Data Scientist?">Skill gap check</button>
                    <button class="suggestion" type="button" data-example="Gợi ý khóa học Machine Learning phù hợp cho người mới.">Course suggestions</button>
                    <button class="suggestion" type="button" data-example="Lộ trình từ fresher lên backend developer như thế nào?">Career path</button>
                </div>
                <div class="input-shell">
                    <textarea id="queryInput" rows="1" placeholder="Ask a career question..." autofocus></textarea>
                    <button class="send-button" type="button" id="sendButton">Send</button>
                </div>
            </footer>
        </main>
    </div>

    <script>
        const state = {
            mode: "agent",
            busy: false,
        };

        const chatArea = document.getElementById("chatArea");
        const messageList = document.getElementById("messageList");
        const input = document.getElementById("queryInput");
        const sendButton = document.getElementById("sendButton");
        const iterSlider = document.getElementById("iterSlider");
        const iterVal = document.getElementById("iterVal");

        function escapeHTML(value) {
            return String(value ?? "")
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }

        function formatText(value) {
            return escapeHTML(value).replace(/\n/g, "<br>");
        }

        function scrollToBottom() {
            chatArea.scrollTop = chatArea.scrollHeight;
        }

        function setBusy(value) {
            state.busy = value;
            sendButton.disabled = value;
            input.disabled = value;
            sendButton.textContent = value ? "Sending..." : "Send";
        }

        function autoSizeInput() {
            input.style.height = "auto";
            input.style.height = `${Math.min(input.scrollHeight, 160)}px`;
        }

        function setMode(mode) {
            state.mode = mode;
            document.querySelectorAll(".mode-card").forEach((button) => {
                button.classList.toggle("is-active", button.dataset.mode === mode);
            });
            input.focus();
        }

        function addUserMessage(text) {
            const node = document.createElement("article");
            node.className = "message user";
            node.innerHTML = `
                <div class="message-head">
                    <span class="label">You</span>
                    <span class="badge">${escapeHTML(state.mode)}</span>
                </div>
                <p>${formatText(text)}</p>
            `;
            messageList.appendChild(node);
            scrollToBottom();
        }

        function addThinkingMessage(label, variant) {
            const node = document.createElement("article");
            node.className = `message ${variant}`;
            node.innerHTML = `
                <div class="message-head">
                    <span class="label">${escapeHTML(label)}</span>
                    <span class="badge">Working</span>
                </div>
                <div class="loader">
                    <span class="dots"><span></span><span></span><span></span></span>
                    <span>Generating response...</span>
                </div>
            `;
            messageList.appendChild(node);
            scrollToBottom();
            return node;
        }

        function stepRow(label, value) {
            if (!value) return "";
            return `
                <div class="trace-row">
                    <span>${escapeHTML(label)}</span>
                    <p>${formatText(value)}</p>
                </div>
            `;
        }

        function renderChatbot(data, node) {
            const hasError = Boolean(data.error);
            node.className = `message chatbot ${hasError ? "error" : ""}`;
            node.innerHTML = `
                <div class="message-head">
                    <span class="label">Chatbot Baseline</span>
                    <span class="badge">No tools</span>
                </div>
                <div class="answer">${formatText(data.error || data.response || "No response returned.")}</div>
            `;
            scrollToBottom();
        }

        function renderAgent(data, node) {
            const steps = Array.isArray(data.steps) ? data.steps : [];
            const traceHTML = steps.map((step, index) => {
                const stepKind = step.final ? "Final" : step.action ? "Tool call" : step.error ? "Error" : "Reasoning";
                return `
                    <details class="trace-step" ${index === 0 || step.final || step.error ? "open" : ""}>
                        <summary>
                            <span>Step ${escapeHTML(step.step ?? index + 1)}</span>
                            <span class="trace-type">${escapeHTML(stepKind)}</span>
                        </summary>
                        <div class="trace-body">
                            ${stepRow("Thought", step.thought)}
                            ${stepRow("Action", step.action)}
                            ${stepRow("Observation", step.observation)}
                            ${stepRow("Final", step.final)}
                            ${stepRow("Error", step.error)}
                        </div>
                    </details>
                `;
            }).join("");

            node.className = "message agent";
            node.innerHTML = `
                <div class="message-head">
                    <span class="label">ReAct Agent</span>
                    <span class="badge">${steps.length} step${steps.length === 1 ? "" : "s"}</span>
                </div>
                <div class="final-card">
                    <div class="label" style="margin-bottom: 8px;">Final answer</div>
                    <div class="answer">${formatText(data.final || "No final answer returned.")}</div>
                </div>
                ${traceHTML ? `<div class="trace">${traceHTML}</div>` : ""}
            `;
            scrollToBottom();
        }

        function renderError(node, label, error) {
            node.className = "message error";
            node.innerHTML = `
                <div class="message-head">
                    <span class="label">${escapeHTML(label)}</span>
                    <span class="badge">Error</span>
                </div>
                <div class="answer">${formatText(error.message || error)}</div>
            `;
            scrollToBottom();
        }

        async function requestChat(mode, query) {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    query,
                    mode,
                    max_iterations: iterSlider.value,
                }),
            });

            const payload = await response.json().catch(() => ({}));
            if (!response.ok) {
                throw new Error(payload.error || `Request failed with status ${response.status}`);
            }
            return payload;
        }

        async function send() {
            const query = input.value.trim();
            if (!query || state.busy) return;

            input.value = "";
            autoSizeInput();
            addUserMessage(query);
            setBusy(true);

            const tasks = [];

            if (state.mode === "chatbot" || state.mode === "both") {
                const node = addThinkingMessage("Chatbot Baseline", "chatbot");
                tasks.push(
                    requestChat("chatbot", query)
                        .then((data) => renderChatbot(data, node))
                        .catch((error) => renderError(node, "Chatbot Baseline", error))
                );
            }

            if (state.mode === "agent" || state.mode === "both") {
                const node = addThinkingMessage("ReAct Agent", "agent");
                tasks.push(
                    requestChat("agent", query)
                        .then((data) => renderAgent(data, node))
                        .catch((error) => renderError(node, "ReAct Agent", error))
                );
            }

            await Promise.allSettled(tasks);
            setBusy(false);
            input.focus();
        }

        function clearChat() {
            messageList.innerHTML = "";
            input.focus();
        }

        document.querySelectorAll(".mode-card").forEach((button) => {
            button.addEventListener("click", () => setMode(button.dataset.mode));
        });

        document.querySelectorAll(".suggestion").forEach((button) => {
            button.addEventListener("click", () => {
                input.value = button.dataset.example;
                autoSizeInput();
                input.focus();
            });
        });

        iterSlider.addEventListener("input", () => {
            iterVal.textContent = iterSlider.value;
        });

        input.addEventListener("input", autoSizeInput);
        input.addEventListener("keydown", (event) => {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                send();
            }
        });

        sendButton.addEventListener("click", send);
        document.getElementById("clearButton").addEventListener("click", clearChat);
        autoSizeInput();
    </script>
</body>
</html>
"""


if __name__ == "__main__":
    print(f"Server: http://localhost:5000 | Provider: {provider.__class__.__name__}")
    app.run(host="0.0.0.0", port=5000, debug=False)
