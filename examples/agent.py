import os
import sys
import json
import subprocess
import yaml
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from providers.utils import openai_client

with open(ROOT / "llm.yaml") as f:
    config = yaml.safe_load(f)

provider = config["provider"]
model = config["model"]

if provider == "local":
    print("Agent requires function calling. Use openai/groq/anthropic/deepseek in llm.yaml.")
    sys.exit(0)

# --- Tools the agent can use ---

def read_file(path):
    try:
        p = Path(path).resolve()
        if not p.is_relative_to(WORKSPACE):
            return f"Blocked: reads outside working directory are not allowed ({p})"
        return p.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error: {e}"

WORKSPACE = Path.cwd().resolve()

def write_file(path, content):
    try:
        p = Path(path).resolve()
        if not p.is_relative_to(WORKSPACE):
            return f"Blocked: writes outside working directory are not allowed ({p})"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Written: {p}"
    except Exception as e:
        return f"Error: {e}"

def run_shell(command):
    print(f"\n  [confirm] run: {command}")
    answer = input("  Allow? [y/N]: ").strip().lower()
    if answer != "y":
        return "Skipped: user declined."
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        out = result.stdout.strip()
        err = result.stderr.strip()
        if result.returncode != 0:
            return f"Exit {result.returncode}\n{err or out}"
        return out or "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: command timed out after 30s"
    except Exception as e:
        return f"Error: {e}"

def list_dir(path="."):
    try:
        p = Path(path).resolve()
        if not p.is_relative_to(WORKSPACE):
            return f"Blocked: listing outside working directory is not allowed ({p})"
        entries = sorted(p.iterdir(), key=lambda e: (e.is_file(), e.name))
        return "\n".join(
            f"{'[dir] ' if e.is_dir() else '      '}{e.name}" for e in entries
        )
    except Exception as e:
        return f"Error: {e}"

tool_map = {
    "read_file": lambda args: read_file(**args),
    "write_file": lambda args: write_file(**args),
    "run_shell": lambda args: run_shell(**args),
    "list_dir": lambda args: list_dir(**args),
}

tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read contents of a file",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "File path"}},
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Create or overwrite a file with given content",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path"},
                    "content": {"type": "string", "description": "File content"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": "Run a shell command and return output",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string", "description": "Shell command"}},
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List files and folders in a directory",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Directory path, default ."}},
                "required": []
            }
        }
    }
]

# --- Agent loop ---

def run_agent_openai(task):
    client = openai_client(provider)
    messages = [
        {"role": "system", "content": "You are a coding agent. Complete tasks by using tools. When done, summarize what you did."},
        {"role": "user", "content": task}
    ]

    for step in range(10):
        response = client.chat.completions.create(
            model=model, messages=messages, tools=tools_schema
        )
        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            if message.content:
                print(f"\nAgent: {message.content}")
            return

        for call in message.tool_calls:
            args = json.loads(call.function.arguments)
            print(f"  → {call.function.name}({args})")
            if call.function.name not in tool_map:
                result = f"Error: unknown tool '{call.function.name}'"
            else:
                result = tool_map[call.function.name](args)
            print(f"    {result[:200]}")
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result
            })

    print("Agent: reached max steps.")

def run_agent_anthropic(task):
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    anthropic_tools = [
        {
            "name": t["function"]["name"],
            "description": t["function"]["description"],
            "input_schema": t["function"]["parameters"]
        }
        for t in tools_schema
    ]

    messages = [{"role": "user", "content": task}]
    system = "You are a coding agent. Complete tasks by using tools. When done, summarize what you did."

    for step in range(10):
        response = client.messages.create(
            model=model, max_tokens=4096,
            system=system,
            tools=anthropic_tools,
            messages=messages
        )

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  → {block.name}({block.input})")
                if block.name not in tool_map:
                    result = f"Error: unknown tool '{block.name}'"
                else:
                    result = tool_map[block.name](block.input)
                print(f"    {result[:200]}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })
            elif block.type == "text" and block.text:
                if response.stop_reason != "tool_use":
                    print(f"\nAgent: {block.text}")

        if response.stop_reason == "end_turn" or not tool_results:
            return

        messages += [
            {"role": "assistant", "content": response.content},
            {"role": "user", "content": tool_results}
        ]

    print("Agent: reached max steps.")

# --- Main ---

print(f"llmkit agent | {provider} / {model}")
print(f"Workspace: {WORKSPACE}")
print("Give me a task (e.g. 'create a hello world script and run it')")
task = input("\nTask: ").strip()
if not task:
    sys.exit(0)

print()
if provider == "anthropic":
    run_agent_anthropic(task)
else:
    run_agent_openai(task)
