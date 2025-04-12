import ollama

def chat_with_llm(prompt: str, model: str = "llama2") -> str:
    # response = ollama.chat(
    #     model=model,
    #     messages=[
    #         {"role": "user", "content": prompt}
    #     ]
    # )
    # return response["message"]["content"]
    # prm = prompt
    # mod = model
    
    if "hints" in prompt:
        return f"You can approach this question this way if you want."    
    elif "errors" in prompt:
        return f"These are the errors in this code."
    elif "test cases" in prompt:
        return f"Here are some testcases for this code."
    else:
        return f"Your code looks fine."