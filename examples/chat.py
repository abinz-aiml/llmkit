import sys
import yaml
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, ".")

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
