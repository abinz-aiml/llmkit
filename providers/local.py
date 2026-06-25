import requests

def send_message(prompt, model="llama3.2"):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=120
        )
        data = response.json()
        if "error" in data:
            raise RuntimeError(f"Ollama error: {data['error']}")
        return data["response"]
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Ollama is not running. Start it with: ollama serve")
    except requests.exceptions.Timeout:
        raise RuntimeError("Ollama timed out. Try a smaller model or increase timeout.")
    except KeyError:
        raise RuntimeError(f"Model '{model}' not found. Pull it with: ollama pull {model}")
