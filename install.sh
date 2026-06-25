#!/bin/bash
set -e

if [ ! -f llm.yaml ]; then
    echo "llm.yaml not found. Copying from llm.yaml.example..."
    cp llm.yaml.example llm.yaml 2>/dev/null || { echo "Error: llm.yaml missing. Create it from the README."; exit 1; }
fi

provider=$(grep 'provider:' llm.yaml | awk '{print $2}')
model=$(grep 'model:' llm.yaml | awk '{print $2}')
ram_gb=$(free -g | awk '/^Mem:/{print $2}')

echo "Provider: $provider | Model: $model | RAM: ${ram_gb}GB"

if [ "$ram_gb" -lt 8 ]; then
    echo "Warning: less than 8GB RAM. Stick to small models like phi4 or llama3.2."
fi

if [ "$provider" = "local" ]; then
    if ! command -v ollama &>/dev/null; then
        echo "Installing Ollama..."
        curl -fsSL https://ollama.com/install.sh | sh
    fi
    echo "Pulling $model..."
    ollama pull "$model"
    pip3 install -r requirements.txt -q 2>/dev/null || pip3 install -r requirements.txt -q --break-system-packages
    echo "Done. Run: python3 examples/chat.py"
else
    pip3 install -r requirements.txt -q 2>/dev/null || pip3 install -r requirements.txt -q --break-system-packages
    if [ ! -f .env ]; then
        cp .env.example .env
        echo "Add your API key to .env then run: python3 examples/chat.py"
    else
        echo "Done. Run: python3 examples/chat.py"
    fi
fi
