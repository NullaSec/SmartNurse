from typing import Dict, Optional, List
import re

class MedicalDecisionTree:
    def __init__(self):
        self.symptom_categories = {
            "emergencias": self._evaluate_emergencias,
            "cardiovascular": self._evaluate_cardio,
            "neurologico": self._evaluate_neuro,
            "respiratorio": self._evaluate_resp,
            "gastrointestinal": self._evaluate_gi,
            "dermatologico": self._evaluate_derma,
            "infeccioso": self._evaluate_infeccao,
            "gineco_obstetrico": self._evaluate_gineco,
            "geral": self._evaluate_general
        }

    def evaluate(self, sintomas: str, historico: str = "", idade: Optional[int] = None) -> Dict:
        sintomas = self._normalize_input(sintomas)
        historico = self._normalize_input(historico)

        for category, evaluator in self.symptom_categories.items():
            result = evaluator(sintomas, historico, idade)
            if result:
                return result

        return self._fallback_assessment()

    def _normalize_input(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text

    # ========== MÉTODOS DE AVALIAÇÃO ==========

    def _evaluate_emergencias(self, sintomas: str, historico: str, idade: int) -> Optional[Dict]:
        emergencias_keywords = [
            "parada cardiaca", "desmaio prolongado", "convulsao",
            "sangramento incontrolavel", "overdose", "queimadura grave",
            "falta de ar severa", "trauma craniano"
        ]

        if any(keyword in sintomas for keyword in emergencias_keywords):
            return {
                "categoria": "emergencias",
                "diagnosticos": ["Emergência médica"],
                "urgencia": "Altíssima",
                "encaminhamento": "Pronto-Socorro",
                "alertas": ["CHAME O SAMU IMEDIATAMENTE - 192"]
            }
        return None

    def _evaluate_cardio(self, sintomas: str, historico: str, idade: int) -> Optional[Dict]:
        cardiac_keywords = [
            "dor no peito", "dor precordial", "palpitacao",
            "taquicardia", "desmaio", "inchaço nas pernas"
        ]

        if any(keyword in sintomas for keyword in cardiac_keywords):
            details = {
                "categoria": "cardiovascular",
                "diagnosticos": [],
                "urgencia": "Alta",
                "encaminhamento": "Cardiologia",
                "alertas": []
            }

            if "dor no peito" in sintomas:
                if "irradia para o braço" in sintomas:
                    details["diagnosticos"].append("Infarto Agudo do Miocárdio")
                    details["alertas"].append("RISCO DE IAM - PRIORIDADE MÁXIMA")
                elif "piora com esforço" in sintomas:
                    details["diagnosticos"].append("Angina Pectoris")

            if any(cond in historico for cond in ["hipertensao", "colesterol", "diabetes"]):
                details["alertas"].append("Paciente com fatores de risco cardiovascular")

            return details
        return None

    def _evaluate_neuro(self, sintomas: str, historico: str, idade: int) -> Optional[Dict]:
        neuro_keywords = [
            "cefaleia", "dor de cabeca intensa", "convulsao",
            "perda de consciencia", "confusao mental", "visao dupla",
            "fraqueza muscular", "formigamento"
        ]

        if any(keyword in sintomas for keyword in neuro_keywords):
            details = {
                "categoria": "neurologico",
                "diagnosticos": [],
                "urgencia": "Alta",
                "encaminhamento": "Neurologia",
                "alertas": []
            }

            if any(palavra in sintomas for palavra in ["dor de cabeca", "cefaleia"]):
                if "intensa" in sintomas and "repentina" in sintomas:
                    details["diagnosticos"].append("Hemorragia Subaracnóidea")
                    details["alertas"].append("Possível aneurisma cerebral - TC URGENTE")
                elif "vomito" in sintomas and "fotofobia" in sintomas:
                    details["diagnosticos"].append("Enxaqueca com Aura")

            if "AVC" in historico or "acidente vascular cerebral" in historico:
                details["alertas"].append("Paciente com histórico de AVC - risco aumentado")

            return details
        return None

    def _evaluate_resp(self, sintomas: str, historico: str, idade: int) -> Optional[Dict]:
        resp_keywords = [
            "falta de ar", "dispneia", "tosse com sangue",
            "sibilo", "dor toracica ao respirar"
        ]

        if any(keyword in sintomas for keyword in resp_keywords):
            details = {
                "categoria": "respiratorio",
                "diagnosticos": [],
                "urgencia": "Média",
                "encaminhamento": "Pneumologia",
                "alertas": []
            }

            if "falta de ar" in sintomas:
                if "esforco" in sintomas:
                    details["diagnosticos"].append("DPOC" if "tabagismo" in historico else "Asma")
                elif "repentina" in sintomas:
                    details["diagnosticos"].append("Tromboembolismo Pulmonar")
                    details["urgencia"] = "Alta"

            return details
        return None

    def _evaluate_gi(self, sintomas: str, historico: str, idade: int) -> Optional[Dict]:
        gi_keywords = [
            "dor abdominal", "vomito", "diarreia",
            "sangue nas fezes", "ictericia", "azia"
        ]

        if any(keyword in sintomas for keyword in gi_keywords):
            details = {
                "categoria": "gastrointestinal",
                "diagnosticos": [],
                "urgencia": "Média",
                "encaminhamento": "Gastroenterologia",
                "alertas": []
            }

            if "dor abdominal" in sintomas:
                if "quadrante superior direito" in sintomas:
                    details["diagnosticos"].append("Colecistite")
                elif "rebote" in sintomas:
                    details["diagnosticos"].append("Apendicite Aguda")
                    details["urgencia"] = "Alta"

            return details
        return None

    def _evaluate_derma(self, sintomas: str, historico: str, idade: int) -> Optional[Dict]:
        derma_keywords = [
            "erupcao cutanea", "prurido", "lesao na pele",
            "vermelhidao", "bolhas", "descamacao"
        ]

        if any(keyword in sintomas for keyword in derma_keywords):
            details = {
                "categoria": "dermatologico",
                "diagnosticos": [],
                "urgencia": "Baixa",
                "encaminhamento": "Dermatologia",
                "alertas": []
            }

            if any(s in sintomas for s in ["pele descamando", "bolhas extensas"]):
                details.update({
                    "diagnosticos": ["Síndrome de Stevens-Johnson (emergência)"],
                    "urgencia": "Alta",
                    "alertas": ["INTERNAÇÃO URGENTE - RISCO DE SEPSE"]
                })
            elif "erupcao" in sintomas and "febre" in sintomas:
                details["diagnosticos"].append("Doença exantemática (avaliar vacinação)")
            
            return details
        return None

    def _evaluate_infeccao(self, sintomas: str, historico: str, idade: int) -> Optional[Dict]:
        infeccao_keywords = [
            "febre alta", "calafrios", "sudorese noturna",
            "linfonodos aumentados", "viagem recente"
        ]

        if any(keyword in sintomas for keyword in infeccao_keywords):
            details = {
                "categoria": "infeccioso",
                "diagnosticos": [],
                "urgencia": "Média",
                "encaminhamento": "Infectologia",
                "alertas": []
            }

            if "febre alta" in sintomas and any(s in sintomas for s in ["confusao", "taquicardia"]):
                details.update({
                    "diagnosticos": ["Sepse (avaliar SOFA score)"],
                    "urgencia": "Alta",
                    "alertas": ["RISCO DE CHOQUE SÉPTICO - INICIAR PROTOCOLO IMEDIATO"]
                })
            elif "viagem recente" in historico:
                details["diagnosticos"].append("Doença tropical (diferencial)")
            
            return details
        return None

    def _evaluate_gineco(self, sintomas: str, historico: str, idade: int) -> Optional[Dict]:
        gineco_keywords = [
            "sangramento vaginal", "dor pelvica", "corrimento",
            "atraso menstrual", "gravidez", "tpm intensa"
        ]

        if any(keyword in sintomas for keyword in gineco_keywords):
            details = {
                "categoria": "gineco_obstetrico",
                "diagnosticos": [],
                "urgencia": "Média",
                "encaminhamento": "Ginecologia" if "gravidez" not in sintomas else "Obstetrícia",
                "alertas": []
            }

            if "gravidez" in historico and any(s in sintomas for s in ["sangramento", "contracoes"]):
                details.update({
                    "diagnosticos": ["Ameaça de aborto" if idade < 40 else "Descolamento prematuro"],
                    "urgencia": "Alta",
                    "alertas": ["RISCO DE PERDA FETAL - ECOGRAFIA URGENTE"]
                })
            elif "dor pelvica intensa" in sintomas:
                details["diagnosticos"].append("Torção de anexo (diferencial)")
            
            if "corrimento" in sintomas:
                details["diagnosticos"].append("Vaginose/Candidose (avaliar exames)")
            
            return details
        return None

    def _evaluate_general(self, sintomas: str, historico: str, idade: int) -> Optional[Dict]:
        general_keywords = [
            "febre", "calafrios", "perda de peso",
            "astenia", "mal estar", "cansaço"
        ]

        if any(keyword in sintomas for keyword in general_keywords):
            details = {
                "categoria": "geral",
                "diagnosticos": [],
                "urgencia": "Baixa",
                "encaminhamento": "Clínico Geral",
                "alertas": []
            }

            if "febre" in sintomas and "diarreia" in sintomas:
                details["diagnosticos"].append("Gastroenterite Aguda")
            elif "febre" in sintomas and "tosse" in sintomas:
                details["diagnosticos"].append("Pneumonia" if idade > 65 else "Bronquite")
            elif "cansaço" in sintomas and "perda de peso" in sintomas:
                details["diagnosticos"].append("Anemia (diferencial)")

            return details
        return None

    def _fallback_assessment(self) -> Dict:
        return {
            "categoria": "indeterminado",
            "diagnosticos": ["Avaliação clínica necessária"],
            "urgencia": "Baixa",
            "encaminhamento": "Clínico Geral",
            "alertas": []
        }