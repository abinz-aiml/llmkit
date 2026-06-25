# llmkit

Run any LLM — local or via API — with one config file. No framework lock-in. Works on Windows, Mac, Linux.

## Install

```bash
# Linux
bash install.sh

# Mac
bash install.mac.sh

# Windows (PowerShell as admin)
./install.ps1
```

## Configure

Edit `llm.yaml`:

```yaml
provider: local       # local | openai | anthropic | groq | together | deepseek | mistral
model: llama3.2       # any model name for the chosen provider
mode: chat
```

For API providers, copy `.env.example` to `.env` and add your key.

## Run

```bash
# Windows
python examples/chat.py

# Mac / Linux
python3 examples/chat.py

# JavaScript (any OS, requires Node)
node examples/chat.js
```

## Local models (via Ollama)

| Model | Command |
|---|---|
| Llama 4 Scout | `model: llama4` |
| Qwen 3 | `model: qwen3` |
| DeepSeek R1 | `model: deepseek-r1` |
| Mistral | `model: mistral` |
| Phi-4 | `model: phi4` |
| Gemma 4 | `model: gemma3` |

## API providers

| Provider | Env key | Fast cheap model |
|---|---|---|
| OpenAI | `OPENAI_API_KEY` | `gpt-4o-mini` |
| Anthropic | `ANTHROPIC_API_KEY` | `claude-3-5-haiku-20241022` |
| Groq | `GROQ_API_KEY` | `llama-3.1-8b-instant` |
| Together | `TOGETHER_API_KEY` | `meta-llama/Llama-3.3-70B-Instruct-Turbo` |
| DeepSeek | `DEEPSEEK_API_KEY` | `deepseek-chat` |
| Mistral | `MISTRAL_API_KEY` | `mistral-small-latest` |

## MCP Agent (connect any tool)

`mcp_agent.py` connects to any [MCP server](https://github.com/modelcontextprotocol/servers) and lets the LLM use its tools automatically — no code changes needed.

**1. Add `mcp_servers` to `llm.yaml`:**

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

**2. Run:**

```bash
python examples/mcp_agent.py
```

The agent connects to each server, discovers its tools, and uses them to complete your task. Works with any MCP-compatible server — filesystem, GitHub, Slack, Postgres, browser, and more.

> Requires Node.js for `npx`-based servers. Install the `mcp` Python package via `pip install mcp`.

## Optional UI (Docker)

```bash
docker compose up
```
Open `http://localhost:3000`

## Add a provider

Drop a file in `providers/` that exports `send_message(prompt, model)`. That's it.

Example — adding a new provider called `myprovider.py`:

```python
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("MYPROVIDER_API_KEY"), base_url="https://api.myprovider.com/v1")

def send_message(prompt, model="my-model"):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

Then set `provider: myprovider` in `llm.yaml` and add `MYPROVIDER_API_KEY` to `.env`.
