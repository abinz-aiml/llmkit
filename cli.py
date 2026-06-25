import os
import sys
import yaml
from dotenv import load_dotenv

load_dotenv()

if len(sys.argv) < 2:
    print("Usage: python cli.py \"your question here\"")
    sys.exit(1)

prompt = " ".join(sys.argv[1:])

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
    print(f"Unknown provider: {provider}")
    sys.exit(1)

print(send_message(prompt, model))
