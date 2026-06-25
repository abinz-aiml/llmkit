import os
import sys
import json
import yaml
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from providers.utils import openai_client

with open(ROOT / "llm.yaml") as f:
    config = yaml.safe_load(f)

provider = config["provider"]
model = config["model"]

if provider == "local":
    print("Function calling requires an API provider. Switch provider in llm.yaml.")
    sys.exit(0)

def get_weather(city):
    return f"Sunny, 72F in {city}."

def calculate(expression):
    allowed = set("0123456789+-*/(). ")
    if not all(c in allowed for c in expression):
        return "Error: invalid characters in expression"
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"

tool_map = {"get_weather": get_weather, "calculate": calculate}

tools_schema = [
    {"type": "function", "function": {
        "name": "get_weather", "description": "Get current weather for a city",
        "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}
    }},
    {"type": "function", "function": {
        "name": "calculate", "description": "Evaluate a math expression like 2+2 or 10*5",
        "parameters": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]}
    }},
]

prompt = input("You: ").strip()
if not prompt:
    sys.exit(0)

if provider == "anthropic":
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    anthropic_tools = [
        {"name": t["function"]["name"], "description": t["function"]["description"],
         "input_schema": t["function"]["parameters"]}
        for t in tools_schema
    ]
    messages = [{"role": "user", "content": prompt}]
    response = client.messages.create(model=model, max_tokens=1024, tools=anthropic_tools, messages=messages)

    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            if block.name not in tool_map:
                print(f"Unknown tool: {block.name}")
                continue
            try:
                result = tool_map[block.name](**block.input)
            except Exception as e:
                result = f"Error: {e}"
            print(f"Tool: {block.name}({block.input}) → {result}")
            tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})
        elif block.type == "text" and block.text:
            print(f"AI: {block.text}")

    if tool_results:
        messages += [
            {"role": "assistant", "content": response.content},
            {"role": "user", "content": tool_results}
        ]
        final = client.messages.create(model=model, max_tokens=1024, tools=anthropic_tools, messages=messages)
        if final.content and final.content[0].type == "text":
            print(f"AI: {final.content[0].text}")

else:
    client = openai_client(provider)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        tools=tools_schema
    )
    message = response.choices[0].message

    if message.tool_calls:
        tool_results = []
        for call in message.tool_calls:
            try:
                args = json.loads(call.function.arguments)
            except Exception as e:
                print(f"Error parsing arguments for {call.function.name}: {e}")
                continue
            if call.function.name not in tool_map:
                print(f"Unknown tool: {call.function.name}")
                continue
            result = tool_map[call.function.name](**args)
            print(f"Tool: {call.function.name}({args}) → {result}")
            tool_results.append({"role": "tool", "tool_call_id": call.id, "content": result})

        if tool_results:
            final = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}, message, *tool_results]
            )
            print(f"AI: {final.choices[0].message.content}")
    else:
        print(f"AI: {message.content}")
