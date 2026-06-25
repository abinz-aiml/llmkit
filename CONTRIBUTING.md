# Contributing to llmkit

## Add a provider

1. Create `providers/yourprovider.py` with one function:

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("YOURPROVIDER_API_KEY"),
    base_url="https://api.yourprovider.com/v1"
)

def send_message(prompt, model="default-model-name"):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

2. Add `YOURPROVIDER_API_KEY=` to `.env.example`

3. Add your provider to the `providers` dict in `examples/chat.py`, the `providers_map` dict in `examples/rag.py`, and the `providers_map` dict in `cli.py`

4. Add a row to the API providers table in `README.md`

5. Open a pull request

## Add an example

Drop a `.py` or `.js` file in `examples/`. It should read `llm.yaml` and work with at least local and one API provider.

## Rules

- No excessive comments — code should explain itself
- Functions under 20 lines
- No new dependencies unless absolutely necessary
- Test it locally before submitting
