#!/bin/bash
set -e

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
    pip3 install -r requirements.txt -q
    echo "Done. Run: python3 examples/chat.py"
else
    pip3 install -r requirements.txt -q
    if [ ! -f .env ]; then
        cp .env.example .env
        echo "Add your API key to .env then run: python3 examples/chat.py"
    else
        echo "Done. Run: python3 examples/chat.py"
    fi
fi
