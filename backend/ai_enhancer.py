import google.generativeai as genai
import os
from typing import Dict

class AIEnhancer:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro')
    
    def enhance_response(self, 
                       diagnosis: Dict, 
                       guidelines: list,
                       symptoms: str) -> str:
        prompt = f"""
        Você é um assistente médico. Explique de forma clara e concisa:

        1. **Possíveis Causas** (baseado em):
           - Sintomas: {symptoms}
           - Diagnóstico inicial: {diagnosis['diagnosticos']}

        2. **Recomendações** (baseado nos protocolos):
           {[g['title'] for g in guidelines]}

        3. **Próximos Passos**:
           - Urgência: {diagnosis['urgencia']}
           - Encaminhamento: {diagnosis['encaminhamento']}

        Use linguagem acessível (máx. 150 palavras).
        Inclua apenas fatos médicos comprovados.
        """
        
        response = self.model.generate_content(prompt)
        return response.text