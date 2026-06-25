import os
import sys
import json
import yaml
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, ".")

with open("llm.yaml") as f:
    config = yaml.safe_load(f)

provider = config["provider"]
model = config["model"]

def get_weather(city):
    return f"Sunny, 72F in {city}."

def calculate(expression):
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"

tool_map = {"get_weather": get_weather, "calculate": calculate}

tools_openai = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a math expression like 2+2 or 10*5",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"]
            }
        }
    }
]

prompt = input("You: ").strip()

if provider == "anthropic":
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    tools_anthropic = [
        {"name": t["function"]["name"], "description": t["function"]["description"], "input_schema": t["function"]["parameters"]}
        for t in tools_openai
    ]
    response = client.messages.create(
        model=model, max_tokens=1024,
        tools=tools_anthropic,
        messages=[{"role": "user", "content": prompt}]
    )
    for block in response.content:
        if block.type == "tool_use":
            result = tool_map[block.name](**block.input)
            print(f"Tool: {block.name}({block.input}) → {result}")
        elif block.type == "text" and block.text:
            print(f"AI: {block.text}")

elif provider == "local":
    print("Note: function calling requires an API provider. Switch provider in llm.yaml.")
    sys.exit(0)

else:
    from openai import OpenAI
    base_urls = {
        "groq":     "https://api.groq.com/openai/v1",
        "deepseek": "https://api.deepseek.com/v1",
        "together": "https://api.together.xyz/v1",
        "mistral":  "https://api.mistral.ai/v1",
    }
    api_keys = {
        "openai":   os.getenv("OPENAI_API_KEY"),
        "groq":     os.getenv("GROQ_API_KEY"),
        "deepseek": os.getenv("DEEPSEEK_API_KEY"),
        "together": os.getenv("TOGETHER_API_KEY"),
        "mistral":  os.getenv("MISTRAL_API_KEY"),
    }
    kwargs = {"api_key": api_keys[provider]}
    if provider in base_urls:
        kwargs["base_url"] = base_urls[provider]

    client = OpenAI(**kwargs)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        tools=tools_openai
    )
    message = response.choices[0].message

    if message.tool_calls:
        tool_results = []
        for call in message.tool_calls:
            args = json.loads(call.function.arguments)
            result = tool_map[call.function.name](**args)
            print(f"Tool: {call.function.name}({args}) → {result}")
            tool_results.append({"role": "tool", "tool_call_id": call.id, "content": result})

        final = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}, message, *tool_results]
        )
        print(f"AI: {final.choices[0].message.content}")
    else:
        print(f"AI: {message.content}")
