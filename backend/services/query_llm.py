import ollama

def chat_with_llm(prompt: str, model: str = "qwen2.5") -> str:
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    print(response["message"]["content"])
    return response["message"]["content"]
    