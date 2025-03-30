#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from decision_trees import MedicalDecisionTree
from singlestore_client import SingleStoreMed
from ai_enhancer import AIEnhancer
import os
import time
import logging
from dotenv import load_dotenv
from typing import Optional

# Configuração
load_dotenv()
logging.basicConfig(
    filename='medical_system.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = FastAPI()

# Configuração CORS para permitir conexão com o frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # URL do seu Vite
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo Pydantic para validação dos dados de entrada
class SymptomsRequest(BaseModel):
    symptoms: str
    history: Optional[str] = "Não informado"
    age: Optional[int] = 0

# Inicialização dos componentes (singleton)
tree = MedicalDecisionTree()
db = SingleStoreMed()
ai = AIEnhancer()

@app.post("/api/triage")
async def perform_triage(request: SymptomsRequest):
    """Endpoint principal para a triagem médica"""
    try:
        # Validação adicional
        if len(request.symptoms.split()) < 3:
            raise HTTPException(status_code=400, detail="Forneça pelo menos 3 palavras para descrever os sintomas")
        
        if request.age < 0:
            raise HTTPException(status_code=400, detail="Idade não pode ser negativa")

        # Processamento (mesma lógica do terminal)
        diagnosis = tree.evaluate(request.symptoms, request.history, request.age)
        medical_info = db.get_medical_info(
            specialty_id=diagnosis['specialty_id'],
            user_query=request.symptoms
        )
        ai_response = ai.enhance_response(
            diagnosis=diagnosis,
            medical_info=medical_info,
            symptoms=request.symptoms
        )

        # Formata a resposta para o frontend
        return {
            "diagnosis": {
                "category": diagnosis['category'],
                "urgency": diagnosis['urgency'],
                "alerts": diagnosis.get('alerts', [])
            },
            "medical_info": {
                "relevant_info": medical_info['relevant_info'][:3],  # Limita a 3 itens
                "sources": [os.path.basename(s) for s in medical_info['sources']],
                "recommendation": medical_info['recommendation']
            },
            "ai_explanation": ai_response,
            "status": "success"
        }

    except Exception as e:
        logging.error(f"Erro na triagem: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Endpoint para verificar se a API está online"""
    return {"status": "healthy", "version": "1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)