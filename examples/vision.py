import os
import sys
import base64
import yaml
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, ".")

with open("llm.yaml") as f:
    config = yaml.safe_load(f)

provider = config["provider"]
model = config["model"]

image_path = input("Image path: ").strip()
question = input("What do you want to know about it? ").strip()

with open(image_path, "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

ext = image_path.split(".")[-1].lower()
mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"

if provider == "local":
    import requests
    res = requests.post("http://localhost:11434/api/generate", json={
        "model": model,
        "prompt": question,
        "images": [image_data],
        "stream": False
    })
    print(f"\nAI: {res.json()['response']}")

elif provider == "anthropic":
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    res = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": mime, "data": image_data}},
            {"type": "text", "text": question}
        ]}]
    )
    print(f"\nAI: {res.content[0].text}")

else:
    from openai import OpenAI
    base_urls = {
        "groq":     "https://api.groq.com/openai/v1",
        "together": "https://api.together.xyz/v1",
    }
    api_keys = {
        "openai":   os.getenv("OPENAI_API_KEY"),
        "groq":     os.getenv("GROQ_API_KEY"),
        "together": os.getenv("TOGETHER_API_KEY"),
    }
    kwargs = {"api_key": api_keys.get(provider, "")}
    if provider in base_urls:
        kwargs["base_url"] = base_urls[provider]
    client = OpenAI(**kwargs)
    res = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{image_data}"}},
            {"type": "text", "text": question}
        ]}]
    )
    print(f"\nAI: {res.choices[0].message.content}")
