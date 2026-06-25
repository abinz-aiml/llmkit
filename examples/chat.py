import os
import sys
import importlib
import yaml
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from providers.utils import API_KEY_NAMES

def check_env_hint(provider):
    if provider == "local":
        found = [k for k in API_KEY_NAMES.values() if os.getenv(k)]
        if found:
            print(f"Hint: found {found[0]} in .env — set provider in llm.yaml to use it\n")

def load_provider():
    with open(ROOT / "llm.yaml") as f:
        config = yaml.safe_load(f)

    provider = config["provider"]
    model = config["model"]

    providers = {
        "local":     "providers.local",
        "openai":    "providers.openai",
        "anthropic": "providers.anthropic",
        "groq":      "providers.groq",
        "together":  "providers.together",
        "deepseek":  "providers.deepseek",
        "mistral":   "providers.mistral",
    }

    if provider not in providers:
        raise ValueError(f"Unknown provider: {provider}")

    mod = importlib.import_module(providers[provider])
    return mod.send_message, model, provider

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
    except Exception as e:
        print(f"Error: {e}")
