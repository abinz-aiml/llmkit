import os
import sys
import importlib
import yaml
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

if len(sys.argv) < 2:
    print("Usage: python cli.py \"your question here\"")
    sys.exit(1)

prompt = " ".join(sys.argv[1:])

with open(ROOT / "llm.yaml") as f:
    config = yaml.safe_load(f)

provider = config["provider"]
model = config["model"]

providers_map = {
    "local": "providers.local", "openai": "providers.openai",
    "anthropic": "providers.anthropic", "groq": "providers.groq",
    "together": "providers.together", "deepseek": "providers.deepseek",
    "mistral": "providers.mistral",
}

if provider not in providers_map:
    print(f"Unknown provider: {provider}")
    sys.exit(1)

send_message = importlib.import_module(providers_map[provider]).send_message
print(send_message(prompt, model))
