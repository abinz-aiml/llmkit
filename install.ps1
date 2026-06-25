if (-not (Test-Path llm.yaml)) {
    if (Test-Path llm.yaml.example) {
        Copy-Item llm.yaml.example llm.yaml
        Write-Host "llm.yaml not found. Copied from llm.yaml.example."
    } else {
        Write-Host "Error: llm.yaml missing. Create it from the README."; exit 1
    }
}

$provider = (Select-String 'provider:' llm.yaml).Line.Split(':')[1].Trim()
$model = (Select-String 'model:' llm.yaml).Line.Split(':')[1].Trim()
$ramGB = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB)

Write-Host "Provider: $provider | Model: $model | RAM: ${ramGB}GB"

if ($ramGB -lt 8) {
    Write-Host "Warning: less than 8GB RAM. Stick to small models like phi4 or llama3.2."
}

if ($provider -eq "local") {
    if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
        Write-Host "Installing Ollama..."
        winget install Ollama.Ollama
        Start-Sleep -Seconds 5
    }
    Write-Host "Pulling $model..."
    ollama pull $model
    pip install -r requirements.txt -q
    Write-Host "Done. Run: python examples/chat.py"
} else {
    pip install -r requirements.txt -q
    if (-not (Test-Path .env)) {
        Copy-Item .env.example .env
        Write-Host "Add your API key to .env then run: python examples/chat.py"
    } else {
        Write-Host "Done. Run: python examples/chat.py"
    }
}
