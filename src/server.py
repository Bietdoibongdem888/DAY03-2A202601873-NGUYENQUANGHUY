"""
🌐 WEB SERVER — Career Guidance Chatbot Demo
Flask API + HTML frontend comparing Chatbot vs ReAct Agent
"""

import sys, os, re, json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
from providers import get_llm_provider
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from tools import AVAILABLE_TOOLS
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)
provider = get_llm_provider()


def parse_react_response(text: str):
    thought = None
    action_name = None
    action_args = None
    final_answer = None
    for line in text.strip().split("\n"):
        line = line.strip()
        if line.lower().startswith("thought:"):
            thought = line.split(":", 1)[1].strip()
        elif line.lower().startswith("action:"):
            action = line.split(":", 1)[1].strip()
            m = re.match(r"(\w+)\s*[\[\(](.+)[\]\)]", action)
            if m:
                action_name = m.group(1)
                raw_args = m.group(2)
                import csv, io
                try:
                    reader = csv.reader(io.StringIO(raw_args), quotechar="'", skipinitialspace=True)
                    args = next(reader)
                    if not args:
                        args = [a.strip().strip("'\"") for a in raw_args.split(",")]
                    action_args = args
                except Exception:
                    action_args = [a.strip().strip("'\"") for a in raw_args.split(",")]
        elif line.lower().startswith("final answer:"):
            final_answer = line.split(":", 1)[1].strip()
            break
    if not final_answer and not action_name and thought:
        final_answer = text.strip()
    return thought, action_name, action_args, final_answer


def execute_tool(name: str, args: list):
    if name in AVAILABLE_TOOLS:
        try:
            return AVAILABLE_TOOLS[name](*args)
        except Exception as e:
            return f"LOI: {str(e)}"
    return f"LOI: Khong tim thay tool '{name}'"


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    query = data.get("query", "")
    mode = data.get("mode", "chatbot")  # chatbot or agent

    if mode == "chatbot":
        try:
            resp = provider.generate(query, system_prompt=CHATBOT_BASELINE_PROMPT)
            return jsonify({"type": "chatbot", "response": resp})
        except Exception as e:
            return jsonify({"type": "chatbot", "error": str(e)}), 500

    else:  # agent mode
        steps = []
        messages = REACT_SYSTEM_PROMPT + f"\nUser question: {query}"
        final = None

        for step in range(1, MAX_ITERATIONS + 1):
            try:
                resp = provider.generate(messages, system_prompt="")
            except Exception as e:
                steps.append({"step": step, "error": str(e)})
                break

            thought, action_name, action_args, final_answer = parse_react_response(resp)

            step_data = {
                "step": step,
                "thought": thought,
                "action": f"{action_name}{action_args}" if action_name else None,
            }

            if final_answer:
                step_data["final"] = final_answer
                steps.append(step_data)
                final = final_answer
                break

            if action_name and action_args:
                obs = execute_tool(action_name, action_args)
                step_data["observation"] = obs
                messages += f"\nAssistant: {resp}"
                messages += f"\nObservation: {obs}"
                messages += "\nWhat next?"
                steps.append(step_data)
            elif not action_name:
                step_data["final"] = resp.strip()
                steps.append(step_data)
                final = resp.strip()
                break

        if not final:
            steps.append({"step": MAX_ITERATIONS, "final": "GUARDRAIL: Reached max iterations."})

        return jsonify({
            "type": "agent",
            "steps": steps,
            "final": final or "Khong the hoan thanh.",
            "tools": list(AVAILABLE_TOOLS.keys()),
        })


HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VinUni — Career Guidance AI</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0f172a; color: #e2e8f0;
            display: flex; height: 100vh;
        }
        .sidebar {
            width: 280px; background: #1e293b; padding: 20px;
            display: flex; flex-direction: column; gap: 16px;
            border-right: 1px solid #334155;
        }
        .sidebar h2 { font-size: 14px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }
        .sidebar .logo { font-size: 20px; font-weight: 700; color: #38bdf8; }
        .sidebar .sub { font-size: 12px; color: #64748b; }
        .sidebar .provider { font-size: 12px; color: #4ade80; }
        .btn {
            padding: 10px 16px; border: none; border-radius: 8px;
            cursor: pointer; font-weight: 600; font-size: 13px;
            transition: all 0.2s;
        }
        .btn-chatbot { background: #334155; color: #e2e8f0; }
        .btn-agent { background: #ea580c; color: white; }
        .btn:hover { opacity: 0.85; transform: translateY(-1px); }
        .btn.active { box-shadow: 0 0 0 2px #38bdf8; }
        .main {
            flex: 1; display: flex; flex-direction: column;
            max-width: calc(100vw - 280px);
        }
        .chat-area {
            flex: 1; overflow-y: auto; padding: 20px;
            display: flex; flex-direction: column; gap: 16px;
        }
        .input-area {
            padding: 16px 20px; background: #1e293b;
            border-top: 1px solid #334155; display: flex; gap: 10px;
        }
        .input-area input {
            flex: 1; padding: 12px 16px; border-radius: 8px;
            border: 1px solid #334155; background: #0f172a;
            color: #e2e8f0; font-size: 14px; outline: none;
        }
        .input-area input:focus { border-color: #38bdf8; }
        .msg { padding: 14px 18px; border-radius: 12px; max-width: 85%; font-size: 14px; line-height: 1.6; animation: fadeIn 0.3s; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        .msg.user { background: #38bdf8; color: #0f172a; align-self: flex-end; font-weight: 500; }
        .msg.agent { background: #ea580c22; border: 1px solid #ea580c44; align-self: flex-start; }
        .msg.chatbot { background: #334155; border: 1px solid #475569; align-self: flex-start; }
        .msg .label { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
        .msg.agent .label { color: #fb923c; }
        .msg.chatbot .label { color: #94a3b8; }
        .msg.user .label { color: #0f172a; }
        .step-box {
            background: #0f172a; border: 1px solid #334155;
            border-radius: 8px; padding: 10px 14px; margin: 6px 0;
            font-size: 12px; font-family: 'Consolas', monospace;
        }
        .step-box .s { color: #4ade80; } .step-box .t { color: #facc15; }
        .step-box .a { color: #38bdf8; } .step-box .o { color: #c084fc; }
        .typing { display: inline-block; width: 8px; height: 14px; background: #38bdf8; animation: blink 0.8s infinite; }
        @keyframes blink { 50% { opacity: 0; } }
    </style>
</head>
<body>
<div class="sidebar">
    <div class="logo">VinUni AI Lab</div>
    <div class="sub">Day 3 — Chatbot vs ReAct Agent</div>
    <div class="provider">{{ provider_name }} ({{ model }})</div>
    <div style="flex:1"></div>
    <h2>SELECT MODE</h2>
    <button class="btn btn-agent active" id="btnAgent" onclick="setMode('agent')">
        🧠 ReAct Agent
    </button>
    <button class="btn btn-chatbot" id="btnChatbot" onclick="setMode('chatbot')">
        💬 Chatbot Baseline
    </button>
    <button class="btn btn-chatbot" onclick="setMode('both')">
        ⚡ Compare Both
    </button>
    <button class="btn btn-chatbot" style="margin-top:10px" onclick="clearChat()">
        🗑 Clear Chat
    </button>
</div>
<div class="main">
    <div class="chat-area" id="chatArea">
        <div class="msg chatbot" style="align-self:center;text-align:center;background:#1e293b;color:#94a3b8;max-width:90%">
            <strong>Welcome to Career Guidance AI</strong><br>
            Ask about job markets, skills, courses, or career paths.<br>
            Try: <em>"Thị trường Data Science ra sao?"</em>
        </div>
    </div>
    <div class="input-area">
        <input type="text" id="queryInput" placeholder="Ask a career question..."
               onkeydown="if(event.key==='Enter')send()" autofocus>
        <button class="btn btn-agent" onclick="send()">Send</button>
    </div>
</div>

<script>
let currentMode = 'agent';

function setMode(m) { currentMode = m;
    document.getElementById('btnAgent').classList.toggle('active', m==='agent'||m==='both');
    document.getElementById('btnChatbot').classList.toggle('active', m==='chatbot'||m==='both');
}

function clearChat() {
    document.getElementById('chatArea').innerHTML = '';
}

function addMsg(text, type, label) {
    const d = document.getElementById('chatArea');
    const m = document.createElement('div');
    m.className = 'msg ' + type;
    m.innerHTML = `<div class="label">${label}</div>${text}`;
    d.appendChild(m);
    d.scrollTop = d.scrollHeight;
}

function addAgentSteps(steps, final) {
    const d = document.getElementById('chatArea');
    const m = document.createElement('div');
    m.className = 'msg agent';
    let html = '<div class="label">🧠 REACT AGENT</div>';
    steps.forEach(s => {
        html += '<div class="step-box">';
        if(s.thought) html += `<span class="t">🧠 Thought:</span> ${s.thought}<br>`;
        if(s.action) html += `<span class="a">🛠️ Action:</span> ${s.action}<br>`;
        if(s.observation) html += `<span class="o">👁️ Observation:</span> ${s.observation}<br>`;
        if(s.final) html += `<span class="s">🏁 Final:</span> ${s.final}`;
        if(s.error) html += `<span style="color:#ef4444">❌ ${s.error}</span>`;
        html += '</div>';
    });
    m.innerHTML = html;
    d.appendChild(m);
    d.scrollTop = d.scrollHeight;
}

async function send() {
    const inp = document.getElementById('queryInput');
    const q = inp.value.trim();
    if(!q) return;
    inp.value = '';
    addMsg(q, 'user', 'YOU');

    if(currentMode === 'both') {
        addMsg('<span class="typing"></span> Thinking...', 'chatbot', '💬 CHATBOT');
        addMsg('<span class="typing"></span> Thinking...', 'agent', '🧠 REACT AGENT');
    } else if(currentMode === 'chatbot') {
        addMsg('<span class="typing"></span> Thinking...', 'chatbot', '💬 CHATBOT');
    } else {
        addMsg('<span class="typing"></span> Thinking...', 'agent', '🧠 REACT AGENT');
    }
    const last = (s) => document.getElementById('chatArea').lastElementChild;

    if(currentMode === 'both' || currentMode === 'chatbot') {
        try {
            const r = await fetch('/api/chat', {
                method:'POST', headers:{'Content-Type':'application/json'},
                body: JSON.stringify({query:q, mode:'chatbot'})
            });
            const d = await r.json();
            const el = currentMode==='both' ? document.getElementById('chatArea').children[document.getElementById('chatArea').children.length-2] : last();
            el.innerHTML = `<div class="label">💬 CHATBOT</div>${d.error||d.response}`;
        } catch(e) {
            last().innerHTML = `<div class="label">💬 CHATBOT</div>Error: ${e}`;
        }
    }

    if(currentMode === 'both' || currentMode === 'agent') {
        try {
            const r = await fetch('/api/chat', {
                method:'POST', headers:{'Content-Type':'application/json'},
                body: JSON.stringify({query:q, mode:'agent'})
            });
            const d = await r.json();
            last().remove();
            addAgentSteps(d.steps, d.final);
        } catch(e) {
            last().innerHTML = `<div class="label">🧠 REACT AGENT</div>Error: ${e}`;
        }
    }
}
</script>
</body>
</html>
"""


if __name__ == "__main__":
    print(f"Server: http://localhost:5000 | Provider: {provider.__class__.__name__}")
    app.run(host="0.0.0.0", port=5000, debug=False)
