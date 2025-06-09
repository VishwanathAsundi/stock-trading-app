import requests
from config import config

def ask_gemini(prompt):
    import google.generativeai as genai
    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    print("ask_gemini response", response.text.strip())
    return response.text.strip()

def ask_groq(prompt):
    headers = {"Authorization": f"Bearer {config.GROQ_API_KEY}"}
    # Replace with actual Groq endpoint and payload
    response = requests.post(
        "https://api.groq.com/v1/validate",  # Placeholder endpoint
        json={"prompt": prompt},
        headers=headers
    )
    print("ask_groq response", response.json())
    return response.json().get("result", "")

def multi_llm_analysis(prompt):
    results = {}
    results["gemini"] = ask_gemini(prompt)
    if config.GROQ_API_KEY:
        results["groq"] = ask_groq(prompt)
    return results

def validate_with_gemini(llm_results, original_prompt):
    validation_prompt = (
        f"Given the following stock analysis responses from different AI models for the prompt:\n"
        f"\"{original_prompt}\"\n\n"
        f"Responses:\n"
        + "\n".join([f"{k}: {v}" for k, v in llm_results.items()])
        + "\n\n"
        "Please validate each response for accuracy and reasonableness. "
        "Summarize the best action and highlight any disagreements or errors."
    )
    return ask_gemini(validation_prompt) 