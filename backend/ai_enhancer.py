import google.generativeai as genai
import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

class AIEnhancer:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def enhance_response(self, diagnosis: Dict, medical_info: Dict, symptoms: str) -> str:
        """Gera explicação contextualizada com IA"""
        try:
            # Prepara contexto
            context = ""
            if medical_info['relevant_info']:
                context = "\n".join(
                    f"Fonte {i+1}: {info['text'][:300]}..."
                    for i, info in enumerate(medical_info['relevant_info'])
                )

            prompt = f"""
            Você é um assistente médico. Sintetize estas informações:

            **Sintomas do Paciente**:
            {symptoms}

            **Diagnóstico do Sistema**:
            - Categoria: {diagnosis['category']}
            - Urgência: {diagnosis['urgency']}
            - Alertas: {', '.join(diagnosis['alerts']) or 'Nenhum'}

            **Informações Relevantes**:
            {context if context else 'Nenhuma informação específica encontrada'}

            **Instruções**:
            1. Explique em linguagem simples (máx. 150 palavras)
            2. Destaque sinais de alerta
            3. Não faça diagnósticos definitivos
            4. Use apenas as informações fornecidas
            """
            
            response = self.model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            print(f"⚠️  Erro na geração da explicação: {str(e)}")
            return "Não foi possível gerar uma explicação automática."