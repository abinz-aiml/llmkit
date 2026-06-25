#!/bin/bash
set -e

provider=$(grep 'provider:' llm.yaml | awk '{print $2}')
model=$(grep 'model:' llm.yaml | awk '{print $2}')
ram_gb=$(( $(sysctl -n hw.memsize) / 1024 / 1024 / 1024 ))

echo "Provider: $provider | Model: $model | RAM: ${ram_gb}GB"

if [ "$ram_gb" -lt 8 ]; then
    echo "Warning: less than 8GB RAM. Stick to small models like phi4 or llama3.2."
fi

if ! command -v brew &>/dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

if [ "$provider" = "local" ]; then
    if ! command -v ollama &>/dev/null; then
        echo "Installing Ollama..."
        brew install ollama
    fi
    ollama serve &>/dev/null &
    sleep 2
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
