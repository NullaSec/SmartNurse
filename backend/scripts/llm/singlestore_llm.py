import singlestoredb as s2
from typing import List, Dict, Optional
import re

class SmartNurseChatbot:
    def __init__(self):
        self.db_config = {
            "host": "svc-3482219c-a389-4079-b18b-d50662524e8a-shared-dml.aws-virginia-6.svc.singlestore.com",
            "port": 3333,
            "user": "guilherme", 
            "password": "HDps2V1ziGncqV5BWSEePEROjKWMUzIt",
            "database": "db_smartnurse"
        }
        self._verify_connection()

    def _verify_connection(self):
        """Verifica se a conexão é válida antes de operar"""
        try:
            conn = s2.connect(**self.db_config)
            conn.close()
            print("✓ Conexão com SingleStore verificada com sucesso")
        except Exception as e:
            print(f"Erro fatal na conexão: {str(e)}")
            print("Por favor verifique:")
            print("- Credenciais no arquivo .env")
            print("- Permissões do usuário")
            print("- Acesso ao IP (pode precisar de whitelist)")
            exit(1)
    
    def analyze_intent(self, query: str) -> str:
        """Versão simplificada e à prova de erros"""
        query = query.lower()
        
        # Padrões simplificados e robustos
        if "quantos pacientes" in query or "número de pacientes" in query:
            return "stats"
        elif "condição do" in query or "diagnóstico do" in query:
            return "medical_condition"
        elif "medicação" in query or "alergia" in query:
            return "patient_medication"
        elif "paciente" in query or "aluno" in query:
            return "patient_search"
        return "general_question"
    
    def execute_query(self, intent: str, query: str) -> Optional[List[Dict]]:
        """Execução segura de queries"""
        try:
            with s2.connect(**self.db_config) as conn:
                with conn.cursor() as cur:
                    if intent == "stats":
                        return self._get_simple_stats(cur)
                    elif intent in ["medical_condition", "patient_medication"]:
                        field = "Medical Condition" if intent == "medical_condition" else "Medication"
                        return self._get_patient_field(cur, query, field)
                    elif intent == "patient_search":
                        return self._search_patient(cur, query)
        except Exception as e:
            print(f"Erro na execução: {str(e)}")
        return None

    def _get_simple_stats(self, cur) -> List[Dict]:
        """Consulta estatísticas simplificada"""
        try:
            cur.execute("SELECT COUNT(*) AS total FROM fake_patients_en")
            columns = [desc[0] for desc in cur.description]
            row = cur.fetchone()
            return [dict(zip(columns, row))] if row else []
        except:
            return []

    def _get_patient_field(self, cur, query: str, field: str) -> List[Dict]:
        """Busca genérica por campos de paciente"""
        try:
            name = query.split("do")[-1].strip()
            cur.execute(
                f"SELECT Name, `{field}` FROM fake_patients_en WHERE LOWER(Name) LIKE %s LIMIT 1",
                (f"%{name.lower()}%",)
            )
            columns = [desc[0] for desc in cur.description]
            row = cur.fetchone()
            return [dict(zip(columns, row))] if row else []
        except:
            return []

    def _search_patient(self, cur, query: str) -> List[Dict]:
        """Busca segura por pacientes"""
        try:
            if query.isdigit():
                cur.execute("SELECT * FROM fake_patients_en WHERE id = %s LIMIT 1", (int(query),))
            else:
                name = query.split("paciente")[-1].strip()
                cur.execute(
                    "SELECT Name, Age, `Medical Condition`, Medication, Allergies "
                    "FROM fake_patients_en WHERE LOWER(Name) LIKE %s LIMIT 5",
                    (f"%{name.lower()}%",)
                )
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]
        except:
            return []

    def format_response(self, results: List[Dict], intent: str) -> str:
        """Formatação robusta"""
        if not results:
            return "Não encontrei informações relevantes."
        
        if intent == "stats":
            return f"Total de pacientes: {results[0].get('total', 'N/A')}"
        
        if intent in ["medical_condition", "patient_medication"]:
            field = "Condição Médica" if intent == "medical_condition" else "Medicação"
            return f"{field} do {results[0].get('Name', 'paciente')}: {results[0].get(field.replace(' ', '_'), 'N/A')}"
        
        # Formato para múltiplos pacientes
        return "\n\n".join(
            f"Nome: {p.get('Name', 'N/A')}\n"
            f"Idade: {p.get('Age', 'N/A')}\n"
            f"Condição: {p.get('Medical_Condition', 'N/A')}\n"
            f"Medicação: {p.get('Medication', 'N/A')}\n"
            f"Alergias: {p.get('Allergies', 'Nenhuma')}"
            for p in results
        )

if __name__ == "__main__":
    try:
        chatbot = SmartNurseChatbot()
        print("\nSistema Hospitalar - Digite sua pergunta ou 'sair'")
        
        while True:
            try:
                user_input = input("\nVocê: ").strip()
                if user_input.lower() in ['sair', 'exit']:
                    break
                
                intent = chatbot.analyze_intent(user_input)
                results = chatbot.execute_query(intent, user_input)
                print("\nAssistente:", chatbot.format_response(results or [], intent))
                
            except KeyboardInterrupt:
                print("\nEncerrando...")
                break
            except Exception as e:
                print(f"\nOcorreu um erro: {str(e)}")
                
    except Exception as e:
        print(f"Erro ao iniciar o sistema: {str(e)}")