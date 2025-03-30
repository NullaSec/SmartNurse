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
            És um assistente médico e o teu trabalho é fazeres o diagnóstico dos pacientes com base nos ficheiros da especialização que encontrares disponíveis na base de dados.
            Caso não consigas aceder a esses ficheiros usa a tua inteligência para formar uma resposta direta onde indiques o que poderá ser o diagnóstico bem como os cuidados a ter e se necessário ações a tomar.
            Faz respostas de 1 parágrafo.
            Caso não consigas aceder aos ficheiros não precisas de informar, já vai ter uma secção que informa
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