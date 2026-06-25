import os

BASE_URLS = {
    "groq":     "https://api.groq.com/openai/v1",
    "deepseek": "https://api.deepseek.com/v1",
    "together": "https://api.together.xyz/v1",
    "mistral":  "https://api.mistral.ai/v1",
}

API_KEY_NAMES = {
    "openai":   "OPENAI_API_KEY",
    "groq":     "GROQ_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "together": "TOGETHER_API_KEY",
    "mistral":  "MISTRAL_API_KEY",
}

def openai_client(provider):
    from openai import OpenAI
    env_var = API_KEY_NAMES.get(provider, "")
    key = os.getenv(env_var) if env_var else None
    if not key:
        hint = env_var if env_var else "unknown provider"
        raise RuntimeError(f"API key not set for '{provider}'. Add {hint} to your .env file.")
    kwargs = {"api_key": key}
    if provider in BASE_URLS:
        kwargs["base_url"] = BASE_URLS[provider]
    return OpenAI(**kwargs)
