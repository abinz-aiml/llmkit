import os
from together import Together

def send_message(prompt, model="meta-llama/Llama-3.3-70B-Instruct-Turbo"):
    client = Together(api_key=os.getenv("TOGETHER_API_KEY"))
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
