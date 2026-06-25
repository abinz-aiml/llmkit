const fs = require("fs");
const readline = require("readline");
const yaml = require("js-yaml");
require("dotenv").config();

const config = yaml.load(fs.readFileSync("llm.yaml", "utf8"));

const API_ENDPOINTS = {
    openai:   "https://api.openai.com/v1/chat/completions",
    groq:     "https://api.groq.com/openai/v1/chat/completions",
    deepseek: "https://api.deepseek.com/v1/chat/completions",
    mistral:  "https://api.mistral.ai/v1/chat/completions",
    together: "https://api.together.xyz/v1/chat/completions",
};

const API_KEYS = {
    openai:   process.env.OPENAI_API_KEY,
    groq:     process.env.GROQ_API_KEY,
    deepseek: process.env.DEEPSEEK_API_KEY,
    mistral:  process.env.MISTRAL_API_KEY,
    together: process.env.TOGETHER_API_KEY,
};

async function sendMessage(prompt) {
    if (config.provider === "local") {
        const res = await fetch("http://localhost:11434/api/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ model: config.model, prompt, stream: false }),
        });
        const data = await res.json();
        return data.response;
    }

    const res = await fetch(API_ENDPOINTS[config.provider], {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${API_KEYS[config.provider]}`,
        },
        body: JSON.stringify({
            model: config.model,
            messages: [{ role: "user", content: prompt }],
        }),
    });

    const data = await res.json();
    return data.choices[0].message.content;
}

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });

console.log(`llmctl | ${config.provider} / ${config.model}`);
console.log("Ctrl+C to exit\n");

function ask() {
    rl.question("You: ", async (input) => {
        if (!input.trim()) return ask();
        const response = await sendMessage(input.trim());
        console.log(`AI: ${response}\n`);
        ask();
    });
}

ask();
