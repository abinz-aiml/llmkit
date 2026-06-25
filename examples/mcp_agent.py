import os
import sys
import json
import asyncio
import shlex
import yaml
from contextlib import AsyncExitStack
from pathlib import Path
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

load_dotenv()

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from providers.utils import openai_client

with open(ROOT / "llm.yaml") as f:
    config = yaml.safe_load(f)

provider = config["provider"]
model = config["model"]
mcp_configs = config.get("mcp_servers", [])

if provider == "local":
    print("MCP agent requires function calling. Use openai/groq/anthropic in llm.yaml.")
    sys.exit(0)

if not mcp_configs:
    print("No mcp_servers defined in llm.yaml. See README for setup.")
    sys.exit(0)


def resolve_env_val(v):
    if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
        return os.environ.get(v[2:-1], "")
    return str(v)


async def connect_servers(stack):
    sessions = {}
    tools = []
    for srv in mcp_configs:
        try:
            parts = shlex.split(srv["command"])
            env = {**os.environ, **{k: resolve_env_val(v) for k, v in srv.get("env", {}).items()}}
            params = StdioServerParameters(command=parts[0], args=parts[1:], env=env)
            read, write = await stack.enter_async_context(stdio_client(params))
            session = await stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            result = await session.list_tools()
        except Exception as e:
            print(f"  {srv.get('name', '<unnamed>')}: failed to connect — {e}")
            continue
        added = 0
        name = srv.get("name", "<unnamed>")
        for tool in result.tools:
            if tool.name in sessions:
                print(f"  Warning: '{tool.name}' from '{name}' conflicts with existing tool, skipping")
                continue
            sessions[tool.name] = session
            tools.append(tool)
            added += 1
        print(f"  {name}: {added} tools")
    return sessions, tools


async def call_tool(name, args, sessions):
    if name not in sessions:
        return f"Error: unknown tool '{name}'"
    result = await sessions[name].call_tool(name, args)
    parts = [c.text for c in (result.content or []) if hasattr(c, "text") and c.text]
    text = "\n".join(parts) if parts else "(no output)"
    return f"Error: {text}" if result.isError else text


def make_openai_schema(tools):
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description or "",
                "parameters": t.inputSchema or {"type": "object", "properties": {}}
            }
        }
        for t in tools
    ]


async def run_loop_openai(task, sessions, tools):
    client = openai_client(provider)
    schema = make_openai_schema(tools)
    messages = [
        {"role": "system", "content": "Complete the task using tools. Summarize when done."},
        {"role": "user", "content": task}
    ]
    for _ in range(10):
        resp = client.chat.completions.create(model=model, messages=messages, tools=schema)
        msg = resp.choices[0].message
        messages.append(msg)
        if not msg.tool_calls:
            if msg.content:
                print(f"\nAgent: {msg.content}")
            return
        for call in msg.tool_calls:
            try:
                args = json.loads(call.function.arguments)
                result = await call_tool(call.function.name, args, sessions)
            except Exception as e:
                args, result = {}, f"Error: {e}"
            print(f"  → {call.function.name}({args})")
            print(f"    {str(result)[:200]}")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    print("Agent: reached max steps.")


async def run_loop_anthropic(task, sessions, tools):
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    schema = [{"name": t.name, "description": t.description or "", "input_schema": t.inputSchema or {"type": "object", "properties": {}}} for t in tools]
    messages = [{"role": "user", "content": task}]
    system = "Complete the task using tools. Summarize when done."
    for _ in range(10):
        resp = client.messages.create(model=model, max_tokens=4096, system=system, tools=schema, messages=messages)
        tool_results = []
        for block in resp.content:
            if block.type == "tool_use":
                print(f"  → {block.name}({block.input})")
                result = await call_tool(block.name, block.input, sessions)
                print(f"    {str(result)[:200]}")
                tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})
            elif block.type == "text" and block.text and resp.stop_reason != "tool_use":
                print(f"\nAgent: {block.text}")
        if resp.stop_reason == "end_turn" or not tool_results:
            return
        messages += [{"role": "assistant", "content": resp.content}, {"role": "user", "content": tool_results}]
    print("Agent: reached max steps.")


async def main():
    print(f"llmkit mcp-agent | {provider} / {model}")
    print("Connecting to MCP servers...")
    async with AsyncExitStack() as stack:
        sessions, tools = await connect_servers(stack)
        if not tools:
            print("No tools discovered. Check that your MCP servers started correctly.")
            return
        print(f"Ready — {len(tools)} tools available\n")
        task = input("Task: ").strip()
        if not task:
            return
        print()
        try:
            if provider == "anthropic":
                await run_loop_anthropic(task, sessions, tools)
            else:
                await run_loop_openai(task, sessions, tools)
        except Exception as e:
            print(f"Error: {e}")


asyncio.run(main())
