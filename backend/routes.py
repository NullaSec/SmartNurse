from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class SintomasRequest(BaseModel):
    sintomas: str
    # latitude e longitude são opcionais para o MVP inicial
    latitude: float | None = None
    longitude: float | None = None

@router.post("/triagem")
async def triagem(request: SintomasRequest):
    # Resposta mockada (substitua pela LLM depois)
    resposta_mockada = {
        "condicoes": ["Enxaqueca", "Desidratação"],
        "urgencia": "media",
        "especialidade": "Clínico Geral",
        "hospitais": []  # A Pessoa 2 preencherá isso depois
    }
    return resposta_mockada