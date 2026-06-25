import os
from mistralai import Mistral

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

def send_message(prompt, model="mistral-small-latest"):
    response = client.chat.complete(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
