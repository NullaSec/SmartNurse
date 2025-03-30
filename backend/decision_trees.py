import os
from typing import Dict, List
import logging
from dotenv import load_dotenv

# Configuração
load_dotenv()
logging.basicConfig(filename='decision_tree.log', level=logging.INFO)

SPECIALTY_MAPPING = {
    "Cardiology": 1,
    "Dermatology": 2,
    "General Surgery": 3,
    "Gynecology and Obstetrics": 4,
    "Psychiatry": 5,
    "Infectious Diseases": 6,
    "Neurology": 7
}

class MedicalDecisionTree:
    def __init__(self):
        self.symptom_map = {
            # Cardiology / Cardiologia
            "chest pain": "Cardiology",
            "dor no peito": "Cardiology",
            "shortness of breath": "Cardiology",
            "falta de ar": "Cardiology",
            "palpitations": "Cardiology",
            "taquicardia": "Cardiology",
            "dizziness": "Cardiology",
            "tontura": "Cardiology",
            "fainting": "Cardiology",
            "desmaio": "Cardiology",
            
            # Neurology / Neurologia
            "headache": "Neurology",
            "dor de cabeça": "Neurology",
            "seizure": "Neurology",
            "convulsão": "Neurology",
            "numbness": "Neurology",
            "formigamento": "Neurology",
            
            # Dermatology / Dermatologia
            "rash": "Dermatology",
            "erupção cutânea": "Dermatology",
            "itching": "Dermatology",
            "coceira": "Dermatology",
            "skin lesion": "Dermatology",
            "lesão na pele": "Dermatology",
            "acne": "Dermatology",
            "psoriasis": "Dermatology",
            "psoríase": "Dermatology",
            "eczema": "Dermatology",
            "pele seca": "Dermatology",
            "dry skin": "Dermatology",
            
            # General Surgery / Cirurgia Geral
            "abdominal pain": "General Surgery",
            "dor abdominal": "General Surgery",
            "appendicitis": "General Surgery",
            "apendicite": "General Surgery",
            "hernia": "General Surgery",
            "hérnia": "General Surgery",
            "gallstones": "General Surgery",
            "pedras na vesícula": "General Surgery",
            "hemorrhoids": "General Surgery",
            "hemorroidas": "General Surgery",
            
            # Gynecology and Obstetrics / Ginecologia e Obstetrícia
            "vaginal bleeding": "Gynecology and Obstetrics",
            "sangramento vaginal": "Gynecology and Obstetrics",
            "pregnancy": "Gynecology and Obstetrics",
            "gravidez": "Gynecology and Obstetrics",
            "menstrual pain": "Gynecology and Obstetrics",
            "cólica menstrual": "Gynecology and Obstetrics",
            "breast pain": "Gynecology and Obstetrics",
            "dor nos seios": "Gynecology and Obstetrics",
            "infertility": "Gynecology and Obstetrics",
            "infertilidade": "Gynecology and Obstetrics",
            
            # Psychiatry / Psiquiatria
            "depression": "Psychiatry",
            "depressão": "Psychiatry",
            "anxiety": "Psychiatry",
            "ansiedade": "Psychiatry",
            "insomnia": "Psychiatry",
            "insônia": "Psychiatry",
            "panic attacks": "Psychiatry",
            "ataques de pânico": "Psychiatry",
            "hallucinations": "Psychiatry",
            "alucinações": "Psychiatry",
            
            # Infectious Diseases / Doenças Infecciosas
            "fever": "Infectious Diseases",
            "febre": "Infectious Diseases",
            "diarrhea": "Infectious Diseases",
            "diarreia": "Infectious Diseases",
            "vomiting": "Infectious Diseases",
            "vômito": "Infectious Diseases",
            "HIV": "Infectious Diseases",
            "hepatitis": "Infectious Diseases",
            "hepatite": "Infectious Diseases",
            "tuberculosis": "Infectious Diseases",
            "tuberculose": "Infectious Diseases",
        }

        # Sintomas de alto risco (urgência máxima)
        self.red_flag_symptoms = {
            "chest pain": "Possible cardiac event",
            "dor no peito": "Possível evento cardíaco",
            "shortness of breath": "Respiratory distress",
            "falta de ar": "Dificuldade respiratória",
            "fainting": "Possible syncope",
            "desmaio": "Possível síncope"
        }

        # Sintomas pediátricos de alto risco
        self.pediatric_red_flags = {
            "chest pain": "Pediatric cardiac concern",
            "dor no peito": "Problema cardíaco pediátrico",
            "lethargy": "Pediatric emergency",
            "letargia": "Emergência pediátrica"
        }

    def _normalize_text(self, text: str) -> str:
        """Normaliza texto para comparação"""
        return text.lower().strip()

    def _identify_symptoms(self, text: str) -> Dict[str, int]:
        """Identifica sintomas e conta ocorrências por especialidade"""
        normalized_text = self._normalize_text(text)
        symptom_counts = {specialty: 0 for specialty in SPECIALTY_MAPPING.keys()}
        
        for symptom, specialty in self.symptom_map.items():
            if self._normalize_text(symptom) in normalized_text:
                symptom_counts[specialty] += 1
                
        return symptom_counts

    def _determine_priority(self, symptoms: List[str], age: int) -> Dict:
        """Determina urgência e alertas"""
        urgency = "Medium"
        alerts = []
        
        # Verifica sintomas de alto risco
        for symptom in symptoms:
            norm_symptom = self._normalize_text(symptom)
            
            # Prioridade pediátrica
            if age < 18:
                for ped_symptom, alert in self.pediatric_red_flags.items():
                    if self._normalize_text(ped_symptom) in norm_symptom:
                        urgency = "High"
                        alerts.append(alert)
            
            # Sintomas gerais de alto risco
            for red_symptom, alert in self.red_flag_symptoms.items():
                if self._normalize_text(red_symptom) in norm_symptom:
                    urgency = "High"
                    alerts.append(alert)
        
        return {"urgency": urgency, "alerts": list(set(alerts))}

    def evaluate(self, symptoms: str, medical_history: str = "", age: int = 0) -> Dict:
        """
        Avalia sintomas e retorna:
        {
            "category": "Specialty",
            "urgency": "High/Medium/Low",
            "alerts": ["alert1", "alert2"],
            "specialty_id": int
        }
        """
        try:
            # Combina sintomas e histórico para análise
            combined_input = f"{symptoms} {medical_history}"
            
            # Contagem de sintomas por especialidade
            symptom_counts = self._identify_symptoms(combined_input)
            total_symptoms = sum(symptom_counts.values())
            
            if total_symptoms == 0:
                logging.warning(f"No recognized symptoms in: {combined_input}")
                return self._fallback_response(age)
            
            # Determina especialidade principal
            primary_specialty = max(symptom_counts.items(), key=lambda x: x[1])[0]
            
            # Urgência e alertas
            priority_info = self._determine_priority(
                symptoms.split(","), 
                age
            )
            
            # Resposta final
            response = {
                "category": primary_specialty,
                "urgency": priority_info["urgency"],
                "alerts": priority_info["alerts"],
                "specialty_id": SPECIALTY_MAPPING[primary_specialty]
            }
            
            logging.info(f"Evaluation complete: {response}")
            return response
            
        except Exception as e:
            logging.error(f"Evaluation error: {str(e)}")
            return self._fallback_response(age)

    def _fallback_response(self, age: int) -> Dict:
        """Resposta para casos indeterminados"""
        return {
            "category": "General Surgery",
            "urgency": "High" if age < 18 else "Medium",
            "alerts": ["Undifferentiated symptoms - needs evaluation"],
            "specialty_id": SPECIALTY_MAPPING["General Surgery"]
        }

# Testes (executar com pytest -v)
def test_cardiac_symptoms():
    tree = MedicalDecisionTree()
    result = tree.evaluate("dor no peito e falta de ar", age=35)
    assert result["category"] == "Cardiology"
    assert result["urgency"] == "High"
    assert "Possível evento cardíaco" in result["alerts"]

def test_pediatric_case():
    tree = MedicalDecisionTree()
    result = tree.evaluate("criança com dor no peito", age=9)
    assert result["category"] == "Cardiology"
    assert result["urgency"] == "High"
    assert "Problema cardíaco pediátrico" in result["alerts"]