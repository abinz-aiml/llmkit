import os
import sys
import yaml
import chromadb
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, ".")

with open("llm.yaml") as f:
    config = yaml.safe_load(f)

provider = config["provider"]
model = config["model"]

def load_docs(folder="docs"):
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"Created docs/ — drop .txt files in there and run again.")
        sys.exit(0)

    chunks = []
    for fname in os.listdir(folder):
        if fname.endswith(".txt"):
            with open(os.path.join(folder, fname)) as f:
                text = f.read()
            for i, para in enumerate(p.strip() for p in text.split("\n\n") if p.strip()):
                chunks.append({"id": f"{fname}_{i}", "text": para})

    if not chunks:
        print("No .txt files found in docs/ — add some and run again.")
        sys.exit(0)

    return chunks

db = chromadb.Client()
collection = db.get_or_create_collection("docs")

chunks = load_docs()
collection.add(
    documents=[c["text"] for c in chunks],
    ids=[c["id"] for c in chunks]
)

query = input("Ask something about your docs: ").strip()
results = collection.query(query_texts=[query], n_results=3)
context = "\n\n".join(results["documents"][0])
prompt = f"Answer based only on the context below.\n\nContext:\n{context}\n\nQuestion: {query}"

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

print(f"\nAI: {send_message(prompt, model)}")
