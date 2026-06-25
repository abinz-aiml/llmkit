import os
import sys
import yaml
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, ".")

API_KEYS = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GROQ_API_KEY", "TOGETHER_API_KEY", "DEEPSEEK_API_KEY", "MISTRAL_API_KEY"]

def check_env_hint(provider):
    if provider == "local":
        found = [k for k in API_KEYS if os.getenv(k)]
        if found:
            print(f"Hint: found {found[0]} in .env — set provider in llm.yaml to use it\n")

def load_provider():
    with open("llm.yaml") as f:
        config = yaml.safe_load(f)

    provider = config["provider"]
    model = config["model"]

    if provider == "local":
        from providers.local import send_message
    elif provider == "openai":
        from providers.openai import send_message
    elif provider == "anthropic":
        from providers.anthropic import send_message
    elif provider == "groq":
        from providers.groq import send_message
    elif provider == "together":
        from providers.together import send_message
    elif provider == "deepseek":
        from providers.deepseek import send_message
    elif provider == "mistral":
        from providers.mistral import send_message
    else:
        raise ValueError(f"Unknown provider: {provider}")

    return send_message, model, provider

send_message, model, provider = load_provider()
check_env_hint(provider)

print(f"llmkit | {provider} / {model}")
print("Ctrl+C to exit\n")

while True:
    try:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        response = send_message(user_input, model)
        print(f"AI: {response}\n")
    except KeyboardInterrupt:
        print("\nBye!")
        break
