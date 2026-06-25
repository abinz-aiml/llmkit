import os
import sys
import base64
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

image_path = input("Image path: ").strip().strip('"')
question = input("What do you want to know about it? ").strip()

if not Path(image_path).exists():
    print(f"File not found: {image_path}")
    sys.exit(1)

with open(image_path, "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

ext = Path(image_path).suffix.lstrip(".").lower()
if not ext:
    print("Error: file has no extension — cannot determine image type.")
    sys.exit(1)
mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"

if provider == "local":
    import requests
    try:
        res = requests.post("http://localhost:11434/api/generate", json={
            "model": model, "prompt": question,
            "images": [image_data], "stream": False
        }, timeout=120)
        data = res.json()
        if "error" in data:
            raise RuntimeError(f"Ollama error: {data['error']}")
        print(f"\nAI: {data['response']}")
    except requests.exceptions.ConnectionError:
        print("Error: Ollama is not running. Start it with: ollama serve")
    except Exception as e:
        print(f"Error: {e}")

elif provider == "anthropic":
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        res = client.messages.create(
            model=model, max_tokens=1024,
            messages=[{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": mime, "data": image_data}},
                {"type": "text", "text": question}
            ]}]
        )
        print(f"\nAI: {res.content[0].text}")
    except Exception as e:
        print(f"Error: {e}")

else:
    try:
        client = openai_client(provider)
        res = client.chat.completions.create(
            model=model,
            max_tokens=1024,
            messages=[{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{image_data}"}},
                {"type": "text", "text": question}
            ]}]
        )
        print(f"\nAI: {res.choices[0].message.content}")
    except Exception as e:
        print(f"Error: {e}")
