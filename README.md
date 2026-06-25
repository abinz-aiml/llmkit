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
python examples/chat.py
# or
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
| Anthropic | `ANTHROPIC_API_KEY` | `claude-haiku-4-5-20251001` |
| Groq | `GROQ_API_KEY` | `llama-3.1-8b-instant` |
| Together | `TOGETHER_API_KEY` | `meta-llama/Llama-3.3-70B-Instruct-Turbo` |
| DeepSeek | `DEEPSEEK_API_KEY` | `deepseek-chat` |
| Mistral | `MISTRAL_API_KEY` | `mistral-small-latest` |

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
