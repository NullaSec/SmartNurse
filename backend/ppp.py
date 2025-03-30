import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

def get_gemini_model(model_name="gemini-1.5-flash"):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    return genai.GenerativeModel(model_name)

# Exemplo de uso:
model = get_gemini_model()
response = model.generate_content("Explique quantum computing como se eu tivesse 5 anos")
print(response.text)