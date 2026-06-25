$provider = (Select-String 'provider:' llm.yaml).Line.Split(':')[1].Trim()
$model = (Select-String 'model:' llm.yaml).Line.Split(':')[1].Trim()

Write-Host "Provider: $provider | Model: $model"

if ($provider -eq "local") {
    if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
        Write-Host "Installing Ollama..."
        winget install Ollama.Ollama
        Start-Sleep -Seconds 3
    }
    Write-Host "Pulling $model..."
    ollama pull $model
    Write-Host ""
    Write-Host "Done. Run: python examples/chat.py"
} else {
    pip install openai anthropic groq together mistralai python-dotenv pyyaml -q
    if (-not (Test-Path .env)) {
        Copy-Item .env.example .env
        Write-Host "Add your API key to .env then run: python examples/chat.py"
    } else {
        Write-Host "Done. Run: python examples/chat.py"
    }
}
