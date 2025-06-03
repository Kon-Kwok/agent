import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")

def call_gemini_llm(prompt, model_name="gemini-1.5-flash", temperature=0.7):
    """
    调用Gemini LLM模型。
    """
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=temperature)
        )
        return response.text
    except Exception as e:
        print(f"调用Gemini LLM失败: {e}")
        return None

def call_gemini_llm_with_messages(messages, model_name="gemini-1.5-flash", temperature=0.7):
    """
    调用Gemini LLM模型，支持消息列表输入。
    """
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            messages,
            generation_config=genai.types.GenerationConfig(temperature=temperature)
        )
        return response.text
    except Exception as e:
        print(f"调用Gemini LLM失败: {e}")
        return None
