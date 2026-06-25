import os
import sys
import math
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

texts = []
print("Enter texts to embed (empty line to finish):")
while True:
    line = input(f"Text {len(texts)+1}: ").strip()
    if not line:
        break
    texts.append(line)

if not texts:
    print("No text entered.")
    sys.exit(0)

def embed_local(texts):
    import requests
    embeddings = []
    for text in texts:
        try:
            res = requests.post("http://localhost:11434/api/embed", json={
                "model": config["model"],
                "input": text
            }, timeout=60)
            data = res.json()
            if "error" in data:
                raise RuntimeError(f"Ollama error: {data['error']}")
            embeddings.append(data["embeddings"][0])
        except requests.exceptions.ConnectionError:
            raise RuntimeError("Ollama is not running. Start it with: ollama serve")
    return embeddings

def embed_api(texts):
    client = openai_client(provider)
    model = "text-embedding-3-small" if provider == "openai" else config["model"]
    res = client.embeddings.create(input=texts, model=model)
    return [item.embedding for item in res.data]

if provider not in ("local", "openai"):
    print(f"Embeddings are only supported for 'local' and 'openai' providers. Got: {provider}")
    sys.exit(1)

embeddings = embed_local(texts) if provider == "local" else embed_api(texts)

print(f"\nGenerated {len(embeddings)} embeddings, {len(embeddings[0])} dimensions each")

if len(embeddings) == 2:
    a, b = embeddings
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x**2 for x in a))
    mag_b = math.sqrt(sum(x**2 for x in b))
    if mag_a == 0 or mag_b == 0:
        print("Cosine similarity: undefined (zero vector)")
    else:
        print(f"Cosine similarity: {dot / (mag_a * mag_b):.4f}")
