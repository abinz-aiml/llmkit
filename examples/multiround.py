import os
import sys
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

def chat(messages):
    if provider == "local":
        import requests
        try:
            res = requests.post("http://localhost:11434/api/chat", json={
                "model": model, "messages": messages, "stream": False
            }, timeout=120)
            data = res.json()
            if "error" in data:
                raise RuntimeError(f"Ollama error: {data['error']}")
            return data["message"]["content"]
        except requests.exceptions.ConnectionError:
            raise RuntimeError("Ollama is not running. Start it with: ollama serve")
        except requests.exceptions.Timeout:
            raise RuntimeError("Ollama timed out. Try a smaller model or increase timeout.")

    elif provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        res = client.messages.create(model=model, max_tokens=1024, messages=messages)
        return res.content[0].text

    else:
        client = openai_client(provider)
        res = client.chat.completions.create(model=model, messages=messages)
        return res.choices[0].message.content

print(f"llmkit | {provider} / {model} | multi-round")
print("Ctrl+C to exit\n")

messages = []
MAX_TURNS = 40

while True:
    try:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        messages.append({"role": "user", "content": user_input})
        if len(messages) > MAX_TURNS * 2:
            messages = messages[-(MAX_TURNS * 2):]
        reply = chat(messages)
        messages.append({"role": "assistant", "content": reply})
        print(f"AI: {reply}\n")
    except KeyboardInterrupt:
        print("\nBye!")
        break
    except Exception as e:
        if messages and messages[-1]["role"] == "user":
            messages.pop()
        print(f"Error: {e}")
