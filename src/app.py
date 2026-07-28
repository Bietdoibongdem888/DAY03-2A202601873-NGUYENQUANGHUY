"""
🚀 CORE AGENT APP (Role 4: Core Developer / Integrator)
Career Guidance Agent — Chatbot Baseline vs ReAct Agent comparison.
"""

import json
import os
import re
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from tools import AVAILABLE_TOOLS, get_job_market, check_skills, search_courses, get_career_path
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider

load_dotenv()


def load_test_cases():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    if not os.path.exists(config_path):
        config_path = "test_cases.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_baseline_chatbot(user_query: str, provider):
    """Chatbot Baseline: LLM without tools."""
    print(f"\n{'='*60}")
    print(f"[CHATBOT BASELINE] Q: {user_query[:80]}...")
    print(f"{'='*60}")
    try:
        response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
        print(f"Answer: {response}")
        return response
    except Exception as e:
        print(f"[Chatbot Error]: {e}")
        return f"Error: {e}"


def parse_react_response(text: str):
    """Parse LLM response for Thought, Action, Final Answer."""
    thought = None
    action = None
    action_name = None
    action_args = None
    final_answer = None

    for line in text.strip().split("\n"):
        line = line.strip()
        if line.lower().startswith("thought:"):
            thought = line.split(":", 1)[1].strip()
        elif line.lower().startswith("action:"):
            action = line.split(":", 1)[1].strip()
            # Parse action_name[args] or action_name['args'] or action_name["args"]
            m = re.match(r"(\w+)\s*[\[\(](.+)[\]\)]", action)
            if m:
                action_name = m.group(1)
                raw_args = m.group(2)
                # Split by comma, but respect quoted strings
                import csv, io
                try:
                    reader = csv.reader(io.StringIO(raw_args), quotechar="'", skipinitialspace=True)
                    args = next(reader)
                    if not args:
                        args = [a.strip().strip("'\"") for a in raw_args.split(",")]
                except Exception:
                    args = [a.strip().strip("'\"") for a in raw_args.split(",")]
                action_args = args
        elif line.lower().startswith("final answer:"):
            final_answer = line.split(":", 1)[1].strip()
            break

    # If no explicit Final Answer but we have thought without action
    if not final_answer and not action and thought:
        final_answer = text.strip()

    return thought, action_name, action_args, final_answer


def execute_tool(name: str, args: list):
    """Execute a tool by name with given arguments."""
    if name in AVAILABLE_TOOLS:
        try:
            func = AVAILABLE_TOOLS[name]
            result = func(*args)
            return result
        except TypeError:
            return f"LOI: Tool '{name}' nhan sai so luong tham so. Expected: {args}"
        except Exception as e:
            return f"LOI: Tool '{name}' gap loi: {str(e)}"
    else:
        available = ", ".join(AVAILABLE_TOOLS.keys())
        return f"LOI: Khong tim thay tool '{name}'. Cac tool co san: {available}"


def run_react_agent(user_query: str, provider):
    """ReAct Agent Loop: Thought -> Action -> Observation -> ... -> Final Answer."""
    print(f"\n{'='*60}")
    print(f"[REACT AGENT] Q: {user_query[:80]}...")
    print(f"{'='*60}")

    messages = REACT_SYSTEM_PROMPT + f"\nUser question: {user_query}"

    for step in range(1, MAX_ITERATIONS + 1):
        print(f"\n--- ReAct Loop Step {step}/{MAX_ITERATIONS} ---")

        try:
            response = provider.generate(messages, system_prompt="")
        except Exception as e:
            print(f"[Agent LLM Error]: {e}")
            continue

        response_text = response
        print(f"LLM:\n{response_text}")

        thought, action_name, action_args, final_answer = parse_react_response(response_text)

        if final_answer:
            print(f"  >> FINAL: {final_answer}")
            return final_answer

        if action_name and action_args:
            print(f"  >> Action: {action_name}{action_args}")
            observation = execute_tool(action_name, action_args)
            print(f"  >> Observation: {observation}")

            messages += f"\nAssistant Response: {response_text}"
            messages += f"\nObservation: {observation}"
            messages += "\nWhat next? Use the format: Thought: ... Action: ... OR Final Answer: ..."

        elif action_name and not action_args:
            print(f"  >> No arguments for '{action_name}'")
            messages += f"\nObservation: Action '{action_name}' requires arguments. Use: tool_name[arg1, arg2]"

        elif not action_name and not final_answer:
            print("  >> [Guard]: No valid Action/Final Answer, retrying...")
            messages += "\nPlease use: Thought: ... Action: tool[args] OR Final Answer: ..."

    # Max iterations reached
    print(f"GUARDRAIL TRIGGERED: Reached max {MAX_ITERATIONS} iterations.")
    return "Xin loi, toi khong the hoan thanh yeu cau trong gioi han buoc xu ly. Vui long thu lai voi cau hoi cu the hon."


def run_all_tests(provider):
    """Run all 5 test cases through both Chatbot and Agent."""
    tests = load_test_cases()
    print(f"Loaded {len(tests)} test cases.")

    results = []
    for test in tests:
        qid = test["id"]
        question = test["question"]
        category = test["category"]

        print(f"\n{'#'*70}")
        print(f"# TEST #{qid} [{category}]")
        print(f"# Question: {question}")
        print(f"{'#'*70}")

        # 1. Baseline Chatbot
        chatbot_response = run_baseline_chatbot(question, provider)

        # 2. ReAct Agent
        agent_response = run_react_agent(question, provider)

        results.append({
            "id": qid,
            "question": question,
            "category": category,
            "chatbot": chatbot_response,
            "agent": agent_response,
        })

    return results


def generate_comparison_report(results):
    """Generate a comparison table between Chatbot and Agent."""
    print(f"\n{'='*80}")
    print("COMPARISON REPORT: CHATBOT BASELINE vs REACT AGENT")
    print(f"{'='*80}")

    for r in results:
        print(f"\n--- Test #{r['id']}: [{r['category']}] ---")
        print(f"Q: {r['question']}")
        print(f"Chatbot: {r['chatbot'][:120]}...")
        print(f"Agent:   {r['agent'][:120]}...")

    print(f"\n{'='*80}")
    print("SUMMARY:")
    print(f"- Chatbot (Level 2): Only uses static LLM knowledge, cannot access real-time data.")
    print(f"- ReAct Agent (Level 3): Uses Thought->Action->Observation loop with tools.")
    print(f"- Agent tools available: {list(AVAILABLE_TOOLS.keys())}")
    print(f"- Guardrail: Max {MAX_ITERATIONS} iterations per query.")
    print(f"{'='*80}")


if __name__ == "__main__":
    print("=" * 60)
    print("VINUNI - LAB 3: CHATBOT vs REACT AGENT")
    print("Career Guidance Agent | Topic: Career Orientation")
    print("=" * 60)

    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Mock Mode")
    print(f"Provider: {provider.__class__.__name__} (Model: {model_name})")

    tests = load_test_cases()
    print(f"Test cases loaded: {len(tests)}")

    # Run all tests
    results = run_all_tests(provider)

    # Generate report
    generate_comparison_report(results)

    print("\nDone! See docs/trace_eval.md for detailed trace logs.")
