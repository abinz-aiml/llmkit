import os
import sys
import yaml
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, ".")

with open("llm.yaml") as f:
    config = yaml.safe_load(f)

provider = config["provider"]
model = config["model"]

def chat(messages):
    if provider == "local":
        import requests
        res = requests.post("http://localhost:11434/api/chat", json={
            "model": model,
            "messages": messages,
            "stream": False
        })
        return res.json()["message"]["content"]

    elif provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        res = client.messages.create(
            model=model, max_tokens=1024,
            messages=messages
        )
        return res.content[0].text

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
        res = client.chat.completions.create(model=model, messages=messages)
        return res.choices[0].message.content

print(f"llmkit | {provider} / {model} | multi-round")
print("Ctrl+C to exit\n")

messages = []

while True:
    try:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        messages.append({"role": "user", "content": user_input})
        reply = chat(messages)
        messages.append({"role": "assistant", "content": reply})
        print(f"AI: {reply}\n")
    except KeyboardInterrupt:
        print("\nBye!")
        break
