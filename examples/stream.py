import os
import sys
import json
import yaml
import requests
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, ".")

with open("llm.yaml") as f:
    config = yaml.safe_load(f)

provider = config["provider"]
model = config["model"]

print(f"llmkit | {provider} / {model} | streaming")
prompt = input("You: ").strip()
print("AI: ", end="", flush=True)

if provider == "local":
    res = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt, "stream": True},
        stream=True
    )
    for line in res.iter_lines():
        if line:
            data = json.loads(line)
            print(data.get("response", ""), end="", flush=True)
            if data.get("done"):
                break

elif provider == "anthropic":
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    with client.messages.stream(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)

else:
    from openai import OpenAI
    base_urls = {
        "groq":     "https://api.groq.com/openai/v1",
        "deepseek": "https://api.deepseek.com/v1",
        "together": "https://api.together.xyz/v1",
        "mistral":  "https://api.mistral.ai/v1",
    }
    api_keys = {
        "openai":   os.getenv("OPENAI_API_KEY"),
        "groq":     os.getenv("GROQ_API_KEY"),
        "deepseek": os.getenv("DEEPSEEK_API_KEY"),
        "together": os.getenv("TOGETHER_API_KEY"),
        "mistral":  os.getenv("MISTRAL_API_KEY"),
    }
    kwargs = {"api_key": api_keys[provider]}
    if provider in base_urls:
        kwargs["base_url"] = base_urls[provider]

    client = OpenAI(**kwargs)
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)

print("\n")
