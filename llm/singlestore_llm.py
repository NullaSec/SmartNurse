import pandas as pd
from pathlib import Path
import ast
from typing import Dict, List, Union
import logging
from pydantic import BaseModel, field_validator
import requests


# Configuração básica
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Modelo de Dados ---
class PatientInfo(BaseModel):
    id: int
    name: str
    age: int
    condition: str
    medication: str
    allergies: list[str] = []  # Valor padrão vazio
    
    @field_validator('allergies', mode='before')
    def parse_allergies(cls, v: Union[str, list]) -> list:
        if isinstance(v, str):
            # Caso 1: String vazia ou "None"
            if not v or v.lower() in ['none', '[]', 'nan']:
                return []
            
            # Caso 2: String que parece lista (ex: "['Penicillin']")
            try:
                parsed = ast.literal_eval(v)
                if isinstance(parsed, list):
                    return [item for item in parsed if item.lower() != 'none']
                return []
            except:
                return []
        return v if v else []  # Garante retornar lista vazia se None

# --- Classe Principal ---
class PatientChatbot:
    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)
        self.patients = self._load_patients()
        self.llm_url = "https://apps.aws-london-novaprd1.svc.singlestore.com:8000/modelasaservice/be6256d4-e658-42fc-8c9e-6a84e5bc619b/v1/completions"
        self.auth_token = "eyJhbGciOiJFUzUxMiIsImtpZCI6IjhhNmVjNWFmLThlNWEtNDQxOS04NmM4LWRkMDkxN2U1YWNlMSIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsibm92YXB1YmxpYyJdLCJleHAiOjE3NDU4MzU2MzcsIm5iZiI6MTc0MzI0MzYzMiwiaWF0IjoxNzQzMjQzNjM3LCJzdWIiOiIyM2VmMGViMy0yZTMwLTQ1MjMtODc3NS1hMWVkZjAzZjAxYWUiLCJlbWFpbCI6ImRyb2RyaWd1ZXNAc2luZ2xlc3RvcmUuY29tIiwiaWRwSUQiOiJiNmQ2YTZiZC04NjYyLTQzYjItYjlkZS1hZjNhMjdlMGZhYzgiLCJlbWFpbFZlcmlmaWVkIjp0cnVlLCJzc29TdWJqZWN0IjoiMjNlZjBlYjMtMmUzMC00NTIzLTg3NzUtYTFlZGYwM2YwMWFlIiwidmFsaWRGb3JQb3J0YWwiOmZhbHNlLCJyZWFkT25seSI6ZmFsc2UsIm5vdmFBcHBJbmZvIjp7InNlcnZpY2VJRCI6ImJlNjI1NmQ0LWU2NTgtNDJmYy04YzllLTZhODRlNWJjNjE5YiIsImFwcElEIjoiN2U3ZTA5YmEtODk4NS00OTFjLWExYTgtM2MzZGNmMmEyN2NjIiwiYXBwVHlwZSI6Ik1vZGVsQXNBU2VydmljZSJ9fQ.ACLa78uadrluTFDbrFqjU88RT9D3CqO4NmbosiG9ZsV7nKJHWDVP6gyZdIsRWGKpqDQE4-GiTEPmpNTjuTZEv4oZAGfzUgIvKFWsdxrWtUDpinjeZ8S5CK14pjocrUsneNTZdee4swYv-N9jJEmOc6y1Tce0-ROCRJS0wanRuZ1HeVgV"


    def _load_patients(self) -> List[PatientInfo]:
        df = pd.read_csv(self.csv_path)
        df['Allergies'] = df['Allergies'].fillna('[]')  # Trata valores NaN
        
        patients = []
        for idx, row in df.iterrows():
            try:
                patients.append(PatientInfo(
                    id=idx,
                    name=row['Name'],
                    age=row['Age'],
                    condition=row['Medical Condition'],
                    medication=row['Medication'],
                    allergies=row['Allergies']  # Será convertido automaticamente
                ))
            except Exception as e:
                logger.warning(f"Paciente {row['Name']} ignorado - erro: {str(e)}")
        
        return patients

    def _ask_llm(self, prompt: str) -> str:
        """Consulta a API LLM"""
        try:
            response = requests.post(
                f"{self.llm_url}?authToken={self.auth_token}",
                json={
                    "model": "unsloth/Meta-Llama-3.1-8B-Instruct",
                    "prompt": prompt,
                    "max_tokens": 150,
                    "temperature": 0.3
                },
                timeout=15,
                verify=False
            )
            return response.json()["choices"][0]["text"].strip()
        except Exception as e:
            logger.error(f"Erro na LLM: {str(e)}")
            return None

    def search_patients(self, **filters) -> List[PatientInfo]:
        """Filtra pacientes por critérios"""
        results = []
        for patient in self.patients:
            match = True
            for key, value in filters.items():
                if key == 'allergies':
                    if not any(allergy.lower() == value.lower() for allergy in patient.allergies):
                        match = False
                elif getattr(patient, key, None) != value:
                    match = False
            if match:
                results.append(patient)
        return results

    def interactive_cli(self):
        """Interface de linha de comando interativa"""
        print("\n💊 Assistente Médico - Consulta de Pacientes")
        print(f"📊 Total de pacientes carregados: {len(self.patients)}")
        
        while True:
            print("\nOpções:")
            print("1. Fazer pergunta sobre todos os pacientes")
            print("2. Buscar pacientes por filtro")
            print("3. Sair")
            
            choice = input("\nSelecione uma opção: ").strip()
            
            if choice == "1":
                question = input("\nDigite sua pergunta médica (ex: 'Quais pacientes têm alergia a Penicilina?'): ")
                self._process_question_for_all(question)
            
            elif choice == "2":
                print("\nFiltros disponíveis: name, age, condition, medication, allergies")
                filter_key = input("Critério de busca (ex: 'allergies'): ").strip()
                filter_value = input(f"Valor para {filter_key} (ex: 'Penicillin'): ").strip()
                
                try:
                    if filter_key == 'age':
                        filter_value = int(filter_value)
                    
                    results = self.search_patients(**{filter_key: filter_value})
                    print(f"\n🔍 {len(results)} pacientes encontrados:")
                    for p in results:
                        print(f"- {p.name} (ID: {p.id}): {p.condition}, Alergias: {', '.join(p.allergies) or 'Nenhuma'}")
                except Exception as e:
                    print(f"❌ Erro na busca: {str(e)}")
            
            elif choice == "3":
                print("Saindo...")
                break
            
            else:
                print("Opção inválida. Tente novamente.")

    def _process_question_for_all(self, question: str):
        """Processa uma pergunta para todos os pacientes"""
        print(f"\n🔍 Processando pergunta: '{question}'")
        print("-" * 50)
        
        for patient in self.patients[:5]:  # Limita aos 5 primeiros para demonstração
            prompt = f"""Paciente: {patient.name}
            - Idade: {patient.age}
            - Condição: {patient.condition}
            - Medicação: {patient.medication}
            - Alergias: {', '.join(patient.allergies) or 'Nenhuma'}
            
            Pergunta: {question}"""
            
            print(f"\nPaciente: {patient.name} (ID: {patient.id})")
            print(f"Alergias: {', '.join(patient.allergies) or 'Nenhuma'}")
            
            # Tenta a LLM primeiro
            response = self._ask_llm(prompt)
            if response:
                print(f"Resposta LLM: {response[:200]}...")  # Limita o tamanho
            else:
                # Fallback manual
                if "alergia" in question.lower():
                    if patient.allergies:
                        print(f"⚠️ Alerta: Este paciente tem alergia a {', '.join(patient.allergies)}")
                    else:
                        print("ℹ️ Este paciente não tem alergias registradas")
                else:
                    print("ℹ️ Consulte o prontuário completo para informações detalhadas")
            
            print("-" * 50)



# --- Execução ---
if __name__ == "__main__":
    csv_path = "fake_patients_en.csv"
    chatbot = PatientChatbot(csv_path)
    
    # Verificação dos primeiros 5 pacientes
    print("\n🔍 Amostra de dados carregados:")
    for p in chatbot.patients[:5]:
        print(f"{p.name}:")
        print(f"  Alergias (tipo {type(p.allergies)}): {p.allergies}")
        print(f"  Medicação: {p.medication}")
        print("-" * 40)
    #chatbot.interactive_cli()