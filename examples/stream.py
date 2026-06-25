import os
import sys
import json
import yaml
import requests
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

print(f"llmkit | {provider} / {model} | streaming")
prompt = input("You: ").strip()
if not prompt:
    sys.exit(0)

print("AI: ", end="", flush=True)

if provider == "local":
    try:
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": True},
            stream=True, timeout=120
        )
        for line in res.iter_lines():
            if line:
                data = json.loads(line)
                print(data.get("response", ""), end="", flush=True)
                if data.get("done"):
                    break
    except requests.exceptions.ConnectionError:
        print("\nError: Ollama is not running. Start it with: ollama serve")

elif provider == "anthropic":
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        with client.messages.stream(
            model=model, max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
    except Exception as e:
        print(f"\nError: {e}")

else:
    try:
        client = openai_client(provider)
        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                print(content, end="", flush=True)
    except Exception as e:
        print(f"\nError: {e}")

print("\n")
