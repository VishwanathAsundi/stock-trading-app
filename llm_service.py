import requests
from config import config
import httpx
import asyncio

async def ask_gemini(prompt):
    import google.generativeai as genai
    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
    # Use run_in_executor to avoid blocking event loop
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, lambda: model.generate_content(prompt))
    print("ask_gemini response", response.text.strip())
    return response.text.strip()

async def ask_groq(prompt):
    headers = {"Authorization": f"Bearer {config.GROQ_API_KEY}"}
    async with httpx.AsyncClient(timeout=8) as client:
        # Replace with actual Groq endpoint and payload
        response = await client.post(
            "https://api.groq.com/v1/validate",  # Placeholder endpoint
            json={"prompt": prompt},
            headers=headers
        )
        print("ask_groq response", response.json())
        return response.json().get("result", "")

async def ask_chatgpt(prompt):
    import openai
    openai.api_key = config.OPENAI_API_KEY
    try:
        # Use run_in_executor to avoid blocking event loop
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512,
                temperature=0.7,
            )
        )
        answer = response.choices[0].message["content"].strip()
        print("ask_chatgpt response", answer)
        return answer
    except Exception as e:
        print("ask_chatgpt error", str(e))
        return f"ChatGPT error: {str(e)}"

async def multi_llm_analysis(prompt):
    tasks = {"gemini": ask_gemini(prompt)}
    if config.GROQ_API_KEY:
        tasks["groq"] = ask_groq(prompt)
    if config.OPENAI_API_KEY:
        tasks["chatgpt"] = ask_chatgpt(prompt)
    results = await asyncio.gather(*tasks.values(), return_exceptions=True)
    return {k: (v if not isinstance(v, Exception) else f"error: {v}") for k, v in zip(tasks.keys(), results)}

def validate_with_gemini(llm_results, original_prompt):
    validation_prompt = (
        f"Given the following stock analysis responses from different AI models for the prompt:\n"
        f'"{original_prompt}"\n\n'
        f"Responses:\n"
        + "\n".join([f"{k}: {v}" for k, v in llm_results.items()])
        + "\n\n"
        "Please validate each response for accuracy and reasonableness. "
        "Summarize the best action and highlight any disagreements or errors."
    )
    # Use the async Gemini call for validation as well
    return asyncio.run(ask_gemini(validation_prompt)) 