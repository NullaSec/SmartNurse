import singlestoredb as s2
from typing import Dict, List, Optional, Tuple
import re

class SmartNurseChatbot:
    def __init__(self):
        self.db_config = {
            "host": "svc-3482219c-a389-4079-b18b-d50662524e8a-shared-dml.aws-virginia-6.svc.singlestore.com",
            "port": 3333,
            "user": "guilherme",
            "password": "JBpaDva5sr8SwuvZhNSEynlSOU8ftxSD",
            "database": "db_smartnurse"
        }
    
    def analyze_intent(self, query: str) -> str:
        """Determina a intenção da pergunta do usuário"""
        query = query.lower()
        
        # Padrões para detecção de intenção
        patterns = {
            "patient_search": r"(paciente|aluno)\s+(?:chamad[oa]|nome|id|com)\s+([^\?]+)|(mostre|dados)\s+do\s+(paciente|aluno)",
            "medical_question": r"(pode tomar|deve usar|é seguro|alergia a|interação com)",
            "stats": r"(quantos|total de|número de)\s+(pacientes|alunos)"
        }
        
        for intent, pattern in patterns.items():
            if re.search(pattern, query):
                return intent
        return "general_question"
    
    def execute_query(self, intent: str, query: str) -> Optional[List[Dict]]:
        """Executa queries baseadas na intenção detectada"""
        try:
            with s2.connect(**self.db_config) as conn:
                with conn.cursor(dictionary=True) as cur:
                    if intent == "patient_search":
                        # Extrai nome/ID da query
                        patient_ref = re.search(
                            r"(paciente|aluno)\s+(?:chamad[oa]|nome|id|com)\s+([^\?]+)|(mostre|dados)\s+do\s+(paciente|aluno)\s+([^\?]+)", 
                            query, 
                            re.IGNORECASE
                        )
                        if patient_ref:
                            search_term = patient_ref.group(2) or patient_ref.group(5)
                            return self._search_patient(cur, search_term.strip())
                    
                    elif intent == "stats":
                        return self._get_statistics(cur)
                    
        except Exception as e:
            print(f"Erro na query: {str(e)}")
        return None
    
    def _search_patient(self, cur, search_term: str) -> List[Dict]:
        """Busca paciente por nome ou ID"""
        if search_term.isdigit():
            cur.execute(
                "SELECT * FROM fake_patients_en WHERE id = %s LIMIT 1",
                (int(search_term),))
        else:
            cur.execute(
                "SELECT * FROM fake_patients_en WHERE LOWER(name) LIKE %s LIMIT 5",
                (f"%{search_term.lower()}%",))
        return cur.fetchall()
    
    def _get_statistics(self, cur) -> List[Dict]:
        """Obtém estatísticas básicas"""
        cur.execute("""
            SELECT 
                COUNT(*) AS total_patients,
                AVG(age) AS avg_age,
                medical_condition AS most_common_condition
            FROM fake_patients_en
            GROUP BY medical_condition
            ORDER BY COUNT(*) DESC
            LIMIT 1
        """)
        return cur.fetchall()

    def format_results(self, results: List[Dict]) -> str:
        """Formata os resultados para exibição"""
        if not results:
            return "Nenhum resultado encontrado."
            
        formatted = []
        for item in results:
            if 'total_patients' in item:  # Caso de estatísticas
                formatted.append(
                    f"Total de Pacientes: {item['total_patients']}\n"
                    f"Idade Média: {item['avg_age']:.1f} anos\n"
                    f"Condição Mais Comum: {item['most_common_condition']}"
                )
            else:  # Caso de pacientes
                patient_info = "\n".join(
                    f"{key}: {value}" for key, value in item.items()
                    if not key.startswith('_')  # Ignora campos internos
                )
                formatted.append(patient_info)
        
        return "\n\n" + "\n---\n".join(formatted) + "\n"

# Exemplo de uso
if __name__ == "__main__":
    chatbot = SmartNurseChatbot()
    
    while True:
        user_input = input("\nVocê: ").strip()
        if user_input.lower() in ['sair', 'exit']:
            break
            
        # 1. Analisar intenção
        intent = chatbot.analyze_intent(user_input)
        print(f"Intenção detectada: {intent}")
        
        # 2. Executar ação conforme intenção
        if intent in ["patient_search", "stats"]:
            results = chatbot.execute_query(intent, user_input)
            print(chatbot.format_results(results))

        else:
            print("(Esta funcionalidade será implementada na integração com a LLM)")
