#!/bin/bash
set -e

provider=$(grep 'provider:' llm.yaml | awk '{print $2}')
model=$(grep 'model:' llm.yaml | awk '{print $2}')

echo "Provider: $provider | Model: $model"

if [ "$provider" = "local" ]; then
    if ! command -v ollama &>/dev/null; then
        echo "Installing Ollama..."
        curl -fsSL https://ollama.com/install.sh | sh
    fi
    echo "Pulling $model..."
    ollama pull "$model"
    echo ""
    echo "Done. Run: python3 examples/chat.py"
else
    pip install openai anthropic groq together mistralai python-dotenv pyyaml -q
    if [ ! -f .env ]; then
        cp .env.example .env
        echo "Add your API key to .env then run: python3 examples/chat.py"
    else
        echo "Done. Run: python3 examples/chat.py"
    fi
fi
