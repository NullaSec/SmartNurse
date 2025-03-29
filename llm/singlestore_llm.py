import requests
from typing import Optional
import urllib.parse

class MedicalLLM:
    def __init__(self):
        self.base_url = "https://apps.aws-virginia-nb2.svc.singlestore.com:8000/modelasaservice/3871e155-3d25-4659-bbd7-5a3a175ae552/v1/completions"
        self.auth_token = "eyJhbGciOiJFUzUxMiIsImtpZCI6IjhhNmVjNWFmLThlNWEtNDQxOS04NmM4LWRkMDkxN2U1YWNlMSIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsibm92YXB1YmxpYyJdLCJleHAiOjE3NDU4Njc1MzAsIm5iZiI6MTc0MzI3NTUyNSwiaWF0IjoxNzQzMjc1NTMwLCJzdWIiOiJiNWVlY2Q3Ni02NTVlLTQyZGUtODI3YS1kYWEyZjIxMGRiOTciLCJlbWFpbCI6InBmZXJuYW5kZXNAc2luZ2xlc3RvcmUuY29tIiwiaWRwSUQiOiJiNmQ2YTZiZC04NjYyLTQzYjItYjlkZS1hZjNhMjdlMGZhYzgiLCJlbWFpbFZlcmlmaWVkIjp0cnVlLCJzc29TdWJqZWN0IjoiYjVlZWNkNzYtNjU1ZS00MmRlLTgyN2EtZGFhMmYyMTBkYjk3IiwidmFsaWRGb3JQb3J0YWwiOmZhbHNlLCJyZWFkT25seSI6ZmFsc2UsIm5vdmFBcHBJbmZvIjp7InNlcnZpY2VJRCI6IjM4NzFlMTU1LTNkMjUtNDY1OS1iYmQ3LTVhM2ExNzVhZTU1MiIsImFwcElEIjoiOGY2NjkyZTQtMmJjOC00OTM4LTk0NzMtOTYwNjc2Y2YzMDhhIiwiYXBwVHlwZSI6Ik1vZGVsQXNBU2VydmljZSJ9fQ.AYmMgEgEuwOhPzUSMoZY94znBBknkDnlIYnCGMkBESe7JGMNv6ZRLUewzjLALKslYB0Q4p3pihSWNmT3znWqA8kgAC7-GH8oUomLJk0g2VaTLDVyqxNXnFrUF9I5y716oRaHQbomfH2Meb0V6RY3Pz_RSk8w1j9ijA34E0oSSsy4FR1i"
        self.model = "unsloth/Meta-Llama-3.1-8B-Instruct"

    def ask_question(self, medical_question: str) -> Optional[str]:
        """Consulta a LLM com autenticação via query parameter"""
        try:
            # Construção da URL com authToken
            url = f"{self.base_url}?authToken={urllib.parse.quote(self.auth_token)}"
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            payload = {
                "model": self.model,
                "prompt": self._build_prompt(medical_question),
                "max_tokens": 200,
                "temperature": 0.3
            }

            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=15,
                verify=False  # Apenas para desenvolvimento!
            )

            if response.status_code == 200:
                return self._parse_response(response.json())
            else:
                print(f"Erro na API (HTTP {response.status_code}): {response.text}")
                return None

        except Exception as e:
            print(f"Erro na consulta: {str(e)}")
            return None

    def _build_prompt(self, question: str) -> str:
        """Constroi prompt médico estruturado"""
        return f"""Você é um assistente médico. Responda de forma:
        - Clara e baseada em evidências
        - Destaque contraindicações com ⚠️

        Pergunta: {question}."""

    def _parse_response(self, response: dict) -> str:
        """Processa a resposta da API"""
        try:
            return response['choices'][0]['text'].strip()
        except (KeyError, IndexError):
            return "Não consegui interpretar a resposta da LLM"

# Exemplo de uso
if __name__ == "__main__":
    llm = MedicalLLM()
    
    while True:
        question = input("\nPergunta médica (ou 'sair'): ").strip()
        if question.lower() in ['sair', 'exit']:
            break
            
        response = llm.ask_question(question)
        print("\nResposta:", response or "Erro ao obter resposta")