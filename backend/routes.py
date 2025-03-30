from typing import Optional
from fastapi import APIRouter

router = APIRouter()

@router.get("/rota-teste")
async def rota_teste():
    return {"mensagem": "Rota GET funcionando"}

@router.get("/usuario/{user_id}")
async def ler_usuario(user_id: int, query: Optional[str] = None):
    return {"user_id": user_id, "query": query}