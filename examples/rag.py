import os
import sys
import importlib
import yaml
import chromadb
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

with open(ROOT / "llm.yaml") as f:
    config = yaml.safe_load(f)

provider = config["provider"]
model = config["model"]

def load_docs(folder=None):
    if folder is None:
        folder = ROOT / "docs"
    folder = Path(folder)
    if not folder.exists():
        folder.mkdir(parents=True)
        print(f"Created docs/ — drop .txt files in there and run again.")
        sys.exit(0)

    chunks = []
    for fname in os.listdir(folder):
        if fname.endswith(".txt"):
            with open(folder / fname) as f:
                text = f.read()
            for i, para in enumerate(p.strip() for p in text.split("\n\n") if p.strip()):
                chunks.append({"id": f"{fname}_{i}", "text": para})

    if not chunks:
        print("No .txt files found in docs/ — add some and run again.")
        sys.exit(0)

    return chunks

db = chromadb.EphemeralClient()
collection = db.get_or_create_collection("docs")

chunks = load_docs()
collection.add(
    documents=[c["text"] for c in chunks],
    ids=[c["id"] for c in chunks]
)

query = input("Ask something about your docs: ").strip()
if not query:
    print("No query entered.")
    sys.exit(0)
results = collection.query(query_texts=[query], n_results=min(3, len(chunks)))
context = "\n\n".join(results["documents"][0])
prompt = f"Answer based only on the context below.\n\nContext:\n{context}\n\nQuestion: {query}"

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
print(f"\nAI: {send_message(prompt, model)}")
