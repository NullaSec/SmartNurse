import pandas as pd
from pathlib import Path
import ast
from typing import List, Dict, Union
import logging
from pydantic import BaseModel, field_validator
import requests

# Configuração
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Modelo de Dados ---
class PatientInfo(BaseModel):
    id: int
    name: str
    age: int
    condition: str
    medication: str
    allergies: List[str] = []
    
    @field_validator('allergies', mode='before')
    def parse_allergies(cls, v: Union[str, List]) -> List[str]:
        if isinstance(v, str):
            if not v or v.lower() in ['none', '[]', 'nan']:
                return []
            try:
                parsed = ast.literal_eval(v)
                return [item for item in (parsed if isinstance(parsed, list) else [parsed]) 
                    if str(item).lower() != 'none']
            except:
                return []
        return v or []

# --- Classe Principal ---
class PatientChatbot:
    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)
        self.patients = self._load_patients()
        self.llm_url = "https://apps.aws-london-novaprd1.svc.singlestore.com:8000/modelasaservice/be6256d4-e658-42fc-8c9e-6a84e5bc619b/v1/completions"
        self.auth_token = "eyJhbGciOiJFUzUxMiIsImtpZCI6IjhhNmVjNWFmLThlNWEtNDQxOS04NmM4LWRkMDkxN2U1YWNlMSIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsibm92YXB1YmxpYyJdLCJleHAiOjE3NDU4MzU2MzcsIm5iZiI6MTc0MzI0MzYzMiwiaWF0IjoxNzQzMjQzNjM3LCJzdWIiOiIyM2VmMGViMy0yZTMwLTQ1MjMtODc3NS1hMWVkZjAzZjAxYWUiLCJlbWFpbCI6ImRyb2RyaWd1ZXNAc2luZ2xlc3RvcmUuY29tIiwiaWRwSUQiOiJiNmQ2YTZiZC04NjYyLTQzYjItYjlkZS1hZjNhMjdlMGZhYzgiLCJlbWFpbFZlcmlmaWVkIjp0cnVlLCJzc29TdWJqZWN0IjoiMjNlZjBlYjMtMmUzMC00NTIzLTg3NzUtYTFlZGYwM2YwMWFlIiwidmFsaWRGb3JQb3J0YWwiOmZhbHNlLCJyZWFkT25seSI6ZmFsc2UsIm5vdmFBcHBJbmZvIjp7InNlcnZpY2VJRCI6ImJlNjI1NmQ0LWU2NTgtNDJmYy04YzllLTZhODRlNWJjNjE5YiIsImFwcElEIjoiN2U3ZTA5YmEtODk4NS00OTFjLWExYTgtM2MzZGNmMmEyN2NjIiwiYXBwVHlwZSI6Ik1vZGVsQXNBU2VydmljZSJ9fQ.ACLa78uadrluTFDbrFqjU88RT9D3CqO4NmbosiG9ZsV7nKJHWDVP6gyZdIsRWGKpqDQE4-GiTEPmpNTjuTZEv4oZAGfzUgIvKFWsdxrWtUDpinjeZ8S5CK14pjocrUsneNTZdee4swYv-N9jJEmOc6y1Tce0-ROCRJS0wanRuZ1HeVgV"  # ← Atualize aqui!

    def _load_patients(self) -> List[PatientInfo]:
        """Carrega todos os pacientes do CSV"""
        df = pd.read_csv(self.csv_path)
        df['Allergies'] = df['Allergies'].fillna('[]')
        
        patients = []
        for idx, row in df.iterrows():
            try:
                patients.append(PatientInfo(
                    id=idx,
                    name=row['Name'],
                    age=row['Age'],
                    condition=row['Medical Condition'],
                    medication=row['Medication'],
                    allergies=row['Allergies']
                ))
            except Exception as e:
                logger.warning(f"Ignorando paciente {row['Name']} - erro: {str(e)}")
        return patients

    def _ask_llm(self, prompt: str) -> str:
        """Consulta a API LLM"""
        try:
            response = requests.post(
                f"{self.llm_url}?authToken={self.auth_token}",
                json={
                    "model": "unsloth/Meta-Llama-3.1-8B-Instruct",
                    "prompt": prompt,
                    "max_tokens": 200,
                    "temperature": 0.3
                },
                timeout=20,
                verify=False
            )
            return response.json()["choices"][0]["text"].strip()
        except Exception as e:
            logger.error(f"Erro na LLM: {str(e)}")
            return None

    def search_patients(self, **filters) -> List[PatientInfo]:
        """Busca pacientes com filtros"""
        results = []
        for patient in self.patients:
            match = True
            for key, value in filters.items():
                attr = getattr(patient, key, None)
                if attr is None:
                    match = False
                elif key == 'allergies':
                    if not any(a.lower() == value.lower() for a in patient.allergies):
                        match = False
                elif str(attr).lower() != str(value).lower():
                    match = False
            if match:
                results.append(patient)
        return results

    def interactive_cli(self):
        """Interface de linha de comando"""
        print(f"\n💊 Assistente Médico - {len(self.patients)} pacientes carregados")
        
        while True:
            print("\nMENU PRINCIPAL:")
            print("1. Buscar pacientes por critérios")
            print("2. Fazer pergunta sobre pacientes")
            print("3. Analisar interações medicamentosas")
            print("4. Sair")
            
            choice = input("Escolha uma opção: ").strip()
            
            if choice == "1":
                self._search_mode()
            elif choice == "2":
                self._question_mode()
            elif choice == "3":
                self._check_medication_interactions()
            elif choice == "4":
                print("Encerrando...")
                break
            else:
                print("Opção inválida. Tente novamente.")

    def _search_mode(self):
        """Modo de busca por filtros"""
        print("\n🔍 BUSCA DE PACIENTES")
        print("Filtros disponíveis: nome, idade, condição, medicação, alergia")
        filter_key = input("Critério (ex: 'alergia'): ").lower().strip()
        filter_value = input("Valor para busca: ").strip()
        
        try:
            if filter_key == "idade":
                filter_value = int(filter_value)
                filter_key = "age"
            
            results = self.search_patients(**{filter_key: filter_value})
            
            print(f"\n📊 {len(results)} pacientes encontrados:")
            for p in results:
                print(f"\nID: {p.id} | Nome: {p.name}")
                print(f"Idade: {p.age} | Condição: {p.condition}")
                print(f"Medicação: {p.medication}")
                print(f"Alergias: {', '.join(p.allergies) or 'Nenhuma'}")
        except Exception as e:
            print(f"❌ Erro na busca: {str(e)}")

    def _question_mode(self):
        """Modo de perguntas sobre pacientes"""
        question = input("\n📝 Sua pergunta médica (ex: 'Quais pacientes têm risco cardíaco?'): ")
        
        print("\n🔍 Resultados:")
        for patient in self.patients[:10]:  # Limite para demonstração
            prompt = f"""Dados do paciente:
            - Nome: {patient.name}
            - Idade: {patient.age}
            - Condição: {patient.condition}
            - Medicação: {patient.medication}
            - Alergias: {', '.join(patient.allergies) or 'Nenhuma'}
            
            Pergunta: {question}"""
            
            print(f"\n➡️ Paciente {patient.name} (ID: {patient.id}):")
            response = self._ask_llm(prompt)
            print(response or "ℹ️ Sem informações adicionais")

    def _check_medication_interactions(self):
        """Verifica interações medicamentosas perigosas"""
        dangerous_interactions = {
            "Warfarin": ["Aspirin", "Ibuprofen"],
            "Furosemide": ["Ibuprofen", "Naproxen"],
            "Metformin": ["Contrast dye"]
        }
        
        print("\n⚠️ VERIFICAÇÃO DE INTERAÇÕES PERIGOSAS")
        
        for patient in self.patients:
            alerts = []
            med = patient.medication.split()[0]  # Pega o nome principal
            
            if med in dangerous_interactions:
                for drug in dangerous_interactions[med]:
                    if drug in patient.allergies:
                        alerts.append(f"{med} + {drug}")
            
            if alerts:
                print(f"\n🚨 Paciente {patient.name} (ID: {patient.id}):")
                print(f"Medicação: {patient.medication}")
                print(f"Alergias: {', '.join(patient.allergies)}")
                print("Interações perigosas:", " | ".join(alerts))

if __name__ == "__main__":
    csv_path = Path(__file__).parent / "fake_patients_en.csv"
    
    if not csv_path.exists():
        print(f"❌ Arquivo não encontrado: {csv_path}")
        exit(1)
    
    chatbot = PatientChatbot(csv_path)
    chatbot.interactive_cli()