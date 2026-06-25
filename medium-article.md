# Run Any LLM Locally in 2 Minutes

*No API key. No cloud. No monthly bill. Just your machine.*

---

I was tired of hitting rate limits at 2am.

You know the feeling — you're deep in a coding session, building something with an LLM, and suddenly OpenAI throttles you. Or you get the bill at the end of the month and wince. Or you're working on something sensitive and you don't want your prompts living on someone else's server.

So I built **llmkit** — a one-command toolkit to run any LLM locally or swap to any API provider by changing a single line.

Here's how fast it is.

---

## Step 1: Clone it

```bash
git clone https://github.com/abinz-aiml/llmkit
cd llmkit
```

## Step 2: Run the installer

```bash
# Windows
./install.ps1

# Mac
bash install.mac.sh

# Linux
bash install.sh
```

That's it. The installer detects your RAM, installs Ollama if you don't have it, and pulls the model automatically.

Output looks like this:

```
Provider: local | Model: llama3.2 | RAM: 31GB
Pulling llama3.2...
Done. Run: python examples/chat.py
```

## Step 3: Talk to it

```bash
python examples/chat.py
```

```
llmkit | local / llama3.2
Ctrl+C to exit

You: explain recursion like I'm 10
AI: Imagine you have a box of chocolates...
```

---

## One config file controls everything

There's only one file you ever need to touch: `llm.yaml`

```yaml
provider: local
model: llama3.2
mode: chat
```

Want to switch to GPT-4? Change two lines:

```yaml
provider: openai
model: gpt-4o-mini
```

Want Groq's free blazing-fast inference? Two lines:

```yaml
provider: groq
model: llama-3.1-8b-instant
```

The examples — chat, streaming, RAG, function calling — all work with any provider. You change the config, nothing else.

---

## What models can you run locally?

If you have a decent laptop or desktop, you can run real models for free:

| Model | RAM needed | Good for |
|---|---|---|
| llama3.2 (3B) | 4GB | Quick tasks |
| qwen3:8b | 6GB | Coding, reasoning |
| deepseek-r1:8b | 6GB | Math, analysis |
| mistral:7b | 5GB | Fast chat |
| qwen3:14b | 10GB | Serious work |

I tested this on a Lenovo Legion with an RTX 5080. qwen3:8b runs smooth and fast — easily beats GPT-3.5 on most tasks.

---

## Streaming works out of the box

```bash
python examples/stream.py
```

Tokens print as they arrive, just like ChatGPT. Works with local models and every API provider.

---

## RAG — ask questions about your own documents

Drop `.txt` files in the `docs/` folder and run:

```bash
python examples/rag.py
```

```
Ask something about your docs: what does our refund policy say?
AI: According to the document, refunds are processed within 5–7 business days...
```

Uses ChromaDB under the hood. No external services, no data leaving your machine.

---

## Function calling

```bash
python examples/tools.py
```

```
You: what is the weather in New York and calculate 99 * 12
Tool: get_weather({'city': 'New York'}) → Sunny, 72F
Tool: calculate({'expression': '99 * 12'}) → 1188
AI: The weather in New York is sunny at 72°F, and 99 × 12 equals 1,188.
```

Works with OpenAI, Anthropic, Groq — any provider that supports tool use.

---

## Paid API providers

Sometimes local isn't enough — you need GPT-4 or Claude for a tough task. llmkit supports all the major providers:

- **OpenAI** — gpt-4o, gpt-4o-mini
- **Anthropic** — claude-sonnet, claude-haiku
- **Groq** — free, insanely fast, llama and deepseek models
- **Together AI** — run 70B+ models cheaply
- **DeepSeek** — best bang for buck on reasoning tasks
- **Mistral** — fast European alternative

Add your key to `.env`, change provider in `llm.yaml`, done.

---

## Adding a new provider takes 10 lines

The whole project is built around a simple idea: every provider is one file that does one thing.

```python
# providers/myprovider.py
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

Set `provider: myprovider` in `llm.yaml`. That's the whole integration.

---

## Why I built it this way

Every other LLM toolkit I found was either too heavy (full workflow engines, databases, Docker required just to say hello) or too thin (just a README linking to Ollama docs).

llmkit sits in the middle. Clone it, run one command, start building. No framework to learn. No abstractions hiding what's happening. The code reads like a human wrote it because a human did — and kept it simple on purpose.

---

## Get started

```bash
git clone https://github.com/abinz-aiml/llmkit
cd llmkit
./install.ps1   # or install.sh / install.mac.sh
python examples/chat.py
```

If this saves you from a rate limit at 2am, give it a ⭐ on GitHub.

**[github.com/abinz-aiml/llmkit](https://github.com/abinz-aiml/llmkit)**
