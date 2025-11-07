import ollama

def chat_with_ollama(model_name, prompt):

    response = ollama.chat(
        model=model_name,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]

def chat_with_ollama_msg(model_name, messages):

    response = ollama.chat(
        model=model_name,
        messages=messages
    )
    return response["message"]["content"]
