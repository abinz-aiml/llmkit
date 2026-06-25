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

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });

console.log(`llmkit | ${config.provider} / ${config.model} | streaming`);

rl.question("You: ", async (prompt) => {
    process.stdout.write("AI: ");

    if (config.provider === "local") {
        const res = await fetch("http://localhost:11434/api/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ model: config.model, prompt, stream: true }),
        });
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const lines = decoder.decode(value).split("\n").filter(Boolean);
            for (const line of lines) {
                const data = JSON.parse(line);
                if (data.response) process.stdout.write(data.response);
            }
        }
    } else {
        const res = await fetch(API_ENDPOINTS[config.provider], {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${API_KEYS[config.provider]}`,
            },
            body: JSON.stringify({
                model: config.model,
                messages: [{ role: "user", content: prompt }],
                stream: true,
            }),
        });
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const lines = decoder.decode(value)
                .split("\n")
                .filter(l => l.startsWith("data: ") && l !== "data: [DONE]");
            for (const line of lines) {
                const data = JSON.parse(line.slice(6));
                const content = data.choices?.[0]?.delta?.content;
                if (content) process.stdout.write(content);
            }
        }
    }

    console.log("\n");
    rl.close();
});
