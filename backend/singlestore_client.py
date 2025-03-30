import singlestoredb as s2
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional
import socket
import time

load_dotenv()

class SingleStoreMed:
    def __init__(self, max_retries: int = 3):
        self.connection_string = self._build_connection_string()
        self.max_retries = max_retries

    def _build_connection_string(self) -> str:
        """Constrói a string de conexão a partir das variáveis de ambiente"""
        return (
            f"{os.getenv('SINGLESTORE_USER')}:{os.getenv('SINGLESTORE_PASSWORD')}@"
            f"{os.getenv('SINGLESTORE_HOST')}:{os.getenv('SINGLESTORE_PORT', '3306')}/"
            f"{os.getenv('SINGLESTORE_DB')}"
        )

    def _test_connection(self) -> bool:
        """Verifica se o host é alcançável"""
        host = os.getenv('SINGLESTORE_HOST')
        port = int(os.getenv('SINGLESTORE_PORT', '3306'))
        try:
            with socket.create_connection((host, port), timeout=5):
                return True
        except (socket.gaierror, socket.timeout):
            return False

    def get_connection(self):
        """Estabelece conexão com retry automático"""
        for attempt in range(self.max_retries):
            try:
                if not self._test_connection():
                    raise ConnectionError("Host não alcançável")
                
                conn = s2.connect(self.connection_string)
                print("✅ Conexão com SingleStore estabelecida")
                return conn
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                print(f"⚠️  Tentativa {attempt + 1} falhou. Reconectando...")
                time.sleep(2 ** attempt)  # Backoff exponencial

    def get_guidelines(self, category: str) -> List[Dict]:
        """Busca protocolos médicos com tratamento de erro"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT title, content, urgency_level 
                        FROM medical_guidelines
                        WHERE category = %s
                        ORDER BY urgency_level DESC
                        LIMIT 5
                    """, (category,))
                    
                    return [{
                        'title': row[0],
                        'content': row[1],
                        'urgency': 'Alta' if row[2] > 7 else 'Média' if row[2] > 3 else 'Baixa'
                    } for row in cursor.fetchall()]
        except Exception as e:
            print(f"⚠️  Erro ao buscar diretrizes: {str(e)}")
            return []  # Retorna lista vazia para o sistema continuar funcionando

# Exemplo de uso seguro
if __name__ == "__main__":
    db = SingleStoreMed()
    print(db.get_guidelines("cardiologia"))