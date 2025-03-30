from fastapi import FastAPI, HTTPException
import httpx
from pydantic import BaseModel
from typing import Optional

import re
import json

app = FastAPI()

# Configurações da LLM (use suas credenciais)
LLM_URL = "https://apps.aws-virginia-nb2.svc.singlestore.com:8000/modelasaservice/3871e155-3d25-4659-bbd7-5a3a175ae552/v1"
LLM_KEY = "eyJhbGciOiJFUzUxMiIsImtpZCI6IjhhNmVjNWFmLThlNWEtNDQxOS04NmM4LWRkMDkxN2U1YWNlMSIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsibm92YXB1YmxpYyJdLCJleHAiOjE3NDU4Njc1MzAsIm5iZiI6MTc0MzI3NTUyNSwiaWF0IjoxNzQzMjc1NTMwLCJzdWIiOiJiNWVlY2Q3Ni02NTVlLTQyZGUtODI3YS1kYWEyZjIxMGRiOTciLCJlbWFpbCI6InBmZXJuYW5kZXNAc2luZ2xlc3RvcmUuY29tIiwiaWRwSUQiOiJiNmQ2YTZiZC04NjYyLTQzYjItYjlkZS1hZjNhMjdlMGZhYzgiLCJlbWFpbFZlcmlmaWVkIjp0cnVlLCJzc29TdWJqZWN0IjoiYjVlZWNkNzYtNjU1ZS00MmRlLTgyN2EtZGFhMmYyMTBkYjk3IiwidmFsaWRGb3JQb3J0YWwiOmZhbHNlLCJyZWFkT25seSI6ZmFsc2UsIm5vdmFBcHBJbmZvIjp7InNlcnZpY2VJRCI6IjM4NzFlMTU1LTNkMjUtNDY1OS1iYmQ3LTVhM2ExNzVhZTU1MiIsImFwcElEIjoiOGY2NjkyZTQtMmJjOC00OTM4LTk0NzMtOTYwNjc2Y2YzMDhhIiwiYXBwVHlwZSI6Ik1vZGVsQXNBU2VydmljZSJ9fQ.AYmMgEgEuwOhPzUSMoZY94znBBknkDnlIYnCGMkBESe7JGMNv6ZRLUewzjLALKslYB0Q4p3pihSWNmT3znWqA8kgAC7-GH8oUomLJk0g2VaTLDVyqxNXnFrUF9I5y716oRaHQbomfH2Meb0V6RY3Pz_RSk8w1j9ijA34E0oSSsy4FR1i"
MODEL_NAME = "unsloth/Meta-Llama-3.1-8B-Instruct"

class SintomasInput(BaseModel):
    sintomas: str
    historico: Optional[str] = None
    idade: Optional[int] = None

@app.post("/pre-diagnostico")
async def pre_diagnostico(data: SintomasInput):
    """
    Endpoint para pré-diagnóstico médico
    """
    # Construir o prompt médico
    prompt = f"""<s>[INST]
    <<SYS>>
    Você é um assistente médico. Sua resposta DEVE SER APENAS UM JSON VÁLIDO, SEM NENHUM TEXTO EXTRA.
    Use este formato EXATO:
    {{
    "diagnosticos": [],
    "urgencia": "",
    "recomendacao": "",
    "encaminhamento": ""
    }}
    NÃO REPITA O PROMPT!
    <</SYS>>

    Dados do paciente:
    - Sintomas: {data.sintomas}
    - Histórico: {data.historico or 'Não informado'}
    - Idade: {data.idade or 'Não informada'}

    [/INST]
    {{"diagnosticos": ["""
    
    try:
        # Construir URL com autenticação
        url = f"{LLM_URL}/completions?authToken={LLM_KEY}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
            url,
            headers={"Content-Type": "application/json"},
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "temperature": 0.1,  # Reduz para menos variação
                "max_tokens": 150,   # Suficiente para o JSON
                "stop": ["</s>"]     # Somente parar no fim do token
            }
        )
            
            # Debug (opcional)
            print("Status Code:", response.status_code)
            print("Resposta LLM:", response.text)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Erro na LLM: {response.text}"
                )
            
            # Processar resposta
            resposta = response.json()
        try:
            # Extrai o primeiro JSON encontrado
            json_str = re.search(r'\{.*?\}', conteudo, re.DOTALL).group()
            # Converte para dict para validar
            json_data = json.loads(json_str)
            conteudo = json.dumps(json_data, ensure_ascii=False)
        except:
            conteudo = '''{
                "diagnosticos": ["Erro na extração"],
                "urgencia": "Alta",
                "recomendacao": "Contate o suporte técnico",
                "encaminhamento": "Administração"
            }'''
        return {
            "resultado": conteudo,
            "status": "sucesso"
        }
            
    except httpx.ReadTimeout:
        raise HTTPException(
            status_code=504,
            detail="Tempo de resposta da LLM excedido"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )

@app.get("/status")
async def health_check():
    return {
        "status": "online",
        "versao": "1.0",
        "llm_conectada": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)