# Task: MCP Agent Support ✓ DONE

## Goal
Add MCP (Model Context Protocol) client support to llmkit.
Let users connect any MCP server via llm.yaml — the agent discovers tools automatically.

## Why
agent.py has 4 hardcoded tools. MCP gives access to 100s of community servers
(filesystem, GitHub, Slack, Postgres, browser, etc.) with zero extra code.
True "Terraform for LLMs" — configure your LLM AND your tools in one file.

## What to build

### 1. llm.yaml schema (optional block)
```yaml
provider: anthropic
model: claude-3-5-haiku-20241022
mcp_servers:
  - name: filesystem
    command: npx -y @modelcontextprotocol/server-filesystem ./
  - name: github
    command: npx -y @modelcontextprotocol/server-github
    env:
      GITHUB_TOKEN: ${GITHUB_TOKEN}
```

### 2. examples/mcp_agent.py (new file, ~80 lines)
- Read `mcp_servers` from llm.yaml (skip gracefully if missing)
- Start each server as a subprocess (stdio transport)
- Call `tools/list` on each server → build tool_schema dynamically
- Run agent loop (same as agent.py) with discovered tools
- Route tool calls to the correct server via `tools/call`
- Support anthropic + openai-compatible providers (same split as agent.py)
- 10-step max loop, workspace guard not needed (MCP servers handle their own sandboxing)

### 3. requirements.txt
Add: `mcp`

### 4. README.md
Add MCP section showing llm.yaml config + one example server command

## Files changed
- `examples/mcp_agent.py` — new
- `requirements.txt` — add `mcp`
- `README.md` — add MCP section
- `llm.yaml` — no change (mcp_servers is optional)

## Code rules (non-negotiable)
- No excessive comments
- Functions under 20 lines
- No over-engineering — if it adds complexity without clear value, skip it
- Simple, human-written code
- local provider → exit with message (no function calling)

## Out of scope
- Don't modify agent.py (keep it as the simple zero-dependency version)
- No MCP server implementation (client only)
- No UI, no config validation schema, no type hints
