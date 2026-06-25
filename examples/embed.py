import os
import sys
import yaml
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, ".")

with open("llm.yaml") as f:
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
        res = requests.post("http://localhost:11434/api/embeddings", json={
            "model": config["model"],
            "prompt": text
        })
        embeddings.append(res.json()["embedding"])
    return embeddings

def embed_openai(texts, model="text-embedding-3-small"):
    from openai import OpenAI
    base_urls = {
        "groq":     "https://api.groq.com/openai/v1",
        "together": "https://api.together.xyz/v1",
    }
    api_keys = {
        "openai":   os.getenv("OPENAI_API_KEY"),
        "together": os.getenv("TOGETHER_API_KEY"),
    }
    kwargs = {"api_key": api_keys.get(provider, "")}
    if provider in base_urls:
        kwargs["base_url"] = base_urls[provider]
    client = OpenAI(**kwargs)
    res = client.embeddings.create(input=texts, model=model)
    return [item.embedding for item in res.data]

embeddings = embed_local(texts) if provider == "local" else embed_openai(texts)

print(f"\nGenerated {len(embeddings)} embeddings")
print(f"Dimensions: {len(embeddings[0])}")

if len(embeddings) == 2:
    import math
    a, b = embeddings
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x**2 for x in a))
    mag_b = math.sqrt(sum(x**2 for x in b))
    similarity = dot / (mag_a * mag_b)
    print(f"Cosine similarity between text 1 and 2: {similarity:.4f}")
