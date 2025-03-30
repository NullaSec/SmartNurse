import os
from typing import Dict, List
import logging
from dotenv import load_dotenv

# Configuração
load_dotenv()
logging.basicConfig(filename='decision_tree.log', level=logging.INFO)

SPECIALTY_MAPPING = {
    "Cardiologia": 1,
    "Dermatologia": 2,
    "Cirurgia Geral": 3,
    "Ginecologia e Obstetricia": 4,
    "Psiquiatria": 5,
    "Doenças e Infeções": 6,
    "Neurologia": 7
}

class MedicalDecisionTree:
    def __init__(self):
        self.symptom_map = {
            # Cardiologia / Cardiologia
            "chest pain": "Cardiologia",
            "dor no peito": "Cardiologia",
            "shortness of breath": "Cardiologia",
            "falta de ar": "Cardiologia",
            "palpitations": "Cardiologia",
            "taquicardia": "Cardiologia",
            "dizziness": "Cardiologia",
            "tontura": "Cardiologia",
            "fainting": "Cardiologia",
            "desmaio": "Cardiologia",
            
            # Neurologia / Neurologia
            "headache": "Neurologia",
            "dor de cabeça": "Neurologia",
            "seizure": "Neurologia",
            "convulsão": "Neurologia",
            "numbness": "Neurologia",
            "formigamento": "Neurologia",
            
            # Dermatologia / Dermatologia
            "rash": "Dermatologia",
            "erupção cutânea": "Dermatologia",
            "itching": "Dermatologia",
            "coceira": "Dermatologia",
            "skin lesion": "Dermatologia",
            "lesão na pele": "Dermatologia",
            "acne": "Dermatologia",
            "psoriasis": "Dermatologia",
            "psoríase": "Dermatologia",
            "eczema": "Dermatologia",
            "pele seca": "Dermatologia",
            "dry skin": "Dermatologia",
            
            # Cirurgia Geral / Cirurgia Geral
            "abdominal pain": "Cirurgia Geral",
            "dor abdominal": "Cirurgia Geral",
            "appendicitis": "Cirurgia Geral",
            "apendicite": "Cirurgia Geral",
            "hernia": "Cirurgia Geral",
            "hérnia": "Cirurgia Geral",
            "gallstones": "Cirurgia Geral",
            "pedras na vesícula": "Cirurgia Geral",
            "hemorrhoids": "Cirurgia Geral",
            "hemorroidas": "Cirurgia Geral",
            
            # Ginecologia e Obstetricia / Ginecologia e Obstetrícia
            "vaginal bleeding": "Ginecologia e Obstetricia",
            "sangramento vaginal": "Ginecologia e Obstetricia",
            "pregnancy": "Ginecologia e Obstetricia",
            "gravidez": "Ginecologia e Obstetricia",
            "menstrual pain": "Ginecologia e Obstetricia",
            "cólica menstrual": "Ginecologia e Obstetricia",
            "breast pain": "Ginecologia e Obstetricia",
            "dor nos seios": "Ginecologia e Obstetricia",
            "infertility": "Ginecologia e Obstetricia",
            "infertilidade": "Ginecologia e Obstetricia",
            
            # Psiquiatria / Psiquiatria
            "depression": "Psiquiatria",
            "depressão": "Psiquiatria",
            "anxiety": "Psiquiatria",
            "ansiedade": "Psiquiatria",
            "insomnia": "Psiquiatria",
            "insônia": "Psiquiatria",
            "panic attacks": "Psiquiatria",
            "ataques de pânico": "Psiquiatria",
            "hallucinations": "Psiquiatria",
            "alucinações": "Psiquiatria",
            
            # Doenças e Infeções / Doenças Infecciosas
            "fever": "Doenças e Infeções",
            "febre": "Doenças e Infeções",
            "diarrhea": "Doenças e Infeções",
            "diarreia": "Doenças e Infeções",
            "vomiting": "Doenças e Infeções",
            "vômito": "Doenças e Infeções",
            "HIV": "Doenças e Infeções",
            "hepatitis": "Doenças e Infeções",
            "hepatite": "Doenças e Infeções",
            "tuberculosis": "Doenças e Infeções",
            "tuberculose": "Doenças e Infeções",
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
        return text.Baixaer().strip()

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
        urgency = "Média"
        alerts = []
        
        # Verifica sintomas de alto risco
        for symptom in symptoms:
            norm_symptom = self._normalize_text(symptom)
            
            # Prioridade pediátrica
            if age < 18:
                for ped_symptom, alert in self.pediatric_red_flags.items():
                    if self._normalize_text(ped_symptom) in norm_symptom:
                        urgency = "Alta"
                        alerts.append(alert)
            
            # Sintomas gerais de alto risco
            for red_symptom, alert in self.red_flag_symptoms.items():
                if self._normalize_text(red_symptom) in norm_symptom:
                    urgency = "Alta"
                    alerts.append(alert)
        
        return {"urgency": urgency, "alerts": list(set(alerts))}

    def evaluate(self, symptoms: str, medical_history: str = "", age: int = 0) -> Dict:
        """
        Avalia sintomas e retorna:
        {
            "category": "Specialty",
            "urgency": "Alta/Média/Baixa",
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
            "category": "Cirurgia Geral",
            "urgency": "Alta" if age < 18 else "Média",
            "alerts": ["Undifferentiated symptoms - needs evaluation"],
            "specialty_id": SPECIALTY_MAPPING["Cirurgia Geral"]
        }

# Testes (executar com pytest -v)
def test_cardiac_symptoms():
    tree = MedicalDecisionTree()
    result = tree.evaluate("dor no peito e falta de ar", age=35)
    assert result["category"] == "Cardiologia"
    assert result["urgency"] == "Alta"
    assert "Possível evento cardíaco" in result["alerts"]

def test_pediatric_case():
    tree = MedicalDecisionTree()
    result = tree.evaluate("criança com dor no peito", age=9)
    assert result["category"] == "Cardiologia"
    assert result["urgency"] == "Alta"
    assert "Problema cardíaco pediátrico" in result["alerts"]