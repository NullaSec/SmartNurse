import singlestoredb as s2
import os
from typing import List, Dict, Optional
from google.generativeai import embed_content
from dotenv import load_dotenv
import logging
import numpy as np

load_dotenv()
logging.basicConfig(filename='rag_processor.log', level=logging.INFO)

class SingleStoreMed:
    def __init__(self):
        self.conn_params = {
            'host': os.getenv('SINGLESTORE_HOST'),
            'port': int(os.getenv('SINGLESTORE_PORT', '3306')),
            'user': os.getenv('SINGLESTORE_USER'),
            'password': os.getenv('SINGLESTORE_PASSWORD'),
            'database': os.getenv('SINGLESTORE_DB')
        }
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')

    def _get_connection(self):
        """Estabelece conexão com tratamento de erros"""
        try:
            return s2.connect(**self.conn_params)
        except Exception as e:
            logging.error(f"Connection failed: {str(e)}")
            raise

    def test_connection(self):
        """Testa a conexão com o banco de dados"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    return result[0] == 1
        except Exception as e:
            logging.error(f"Connection test failed: {str(e)}")
            return False

    def _generate_query_embedding(self, query: str) -> Optional[List[float]]:
        """Gera embedding para a consulta do usuário"""
        try:
            result = embed_content(
                model="models/embedding-001",
                content=query,
                task_type="retrieval_query",
                key=self.gemini_api_key
            )
            return result['embedding']
        except Exception as e:
            logging.error(f"Embedding generation failed: {str(e)}")
            return None

    def _search_embeddings(self, doc_ids: List[int], query_embedding: List[float], top_k: int = 3) -> List[Dict]:
        """Realiza busca vetorial nos documentos relevantes"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Converter para formato binário do SingleStore
                    query_embedding_bytes = bytes(np.array(query_embedding, dtype=np.float32).tobytes())
                    
                    query = f"""
                        SELECT 
                            e.id, 
                            e.document_id, 
                            d.texto_extraido,
                            DOT_PRODUCT(e.embedding, JSON_ARRAY_PACK(%s)) AS similarity
                        FROM pdf_embeddings e
                        JOIN documentos_pdf d ON e.document_id = d.id
                        WHERE d.especialidade_id = %s
                        ORDER BY similarity DESC
                        LIMIT %s
                    """
                    
                    cursor.execute(query, (str(query_embedding), top_k))
                    
                    return [{
                        'content': row[2],
                        'source': row[1],
                        'score': float(row[3])
                    } for row in cursor.fetchall()]

        except Exception as e:
            logging.error(f"Vector search failed: {str(e)}")
            return []

    def get_medical_info(self, specialty_id: int, user_query: str) -> Dict:
        """Fluxo completo de busca médica com RAG"""
        response = {
            'relevant_info': [],
            'sources': set(),
            'recommendation': "Consulta um médico presencialmente para avaliação detalhada."
        }

        try:
            # 1. Busca documentos da especialidade
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT id FROM documentos_pdf WHERE especialidade_id = %s",
                        (specialty_id,)
                    )
                    doc_ids = [row[0] for row in cursor.fetchall()]

            if not doc_ids:
                logging.warning(f"No documents found for specialty ID {specialty_id}")
                response['recommendation'] = "Nenhum protocolo encontrado. Dirija-se imediatamente a um hospital."
                return response

            # 2. Gera embedding da consulta
            query_embedding = self._generate_query_embedding(user_query)
            if not query_embedding:
                raise ValueError("Failed to generate query embedding")

            # 3. Busca semântica nos chunks relevantes
            results = self._search_embeddings(doc_ids, query_embedding)
            
            if not results:
                response['recommendation'] = ("Informação não encontrada. "
                    "Procure atendimento médico urgente.")
                return response

            # 4. Processa resultados
            threshold = 0.75  # Ajuste conforme necessidade
            for result in results:
                if result['score'] >= threshold:
                    response['relevant_info'].append({
                        'text': result['content'],
                        'confidence': f"{result['score']:.0%}"
                    })
                    response['sources'].add(result['source'])

            if not response['relevant_info']:
                response['recommendation'] = ("Informação inconclusiva. "
                    "Recomendamos avaliação presencial urgente.")

            return response

        except Exception as e:
            logging.error(f"Medical info retrieval failed: {str(e)}")
            response['recommendation'] = ("Erro no sistema. "
                "Por segurança, dirija-se ao hospital mais próximo.")
            return response

# Exemplo de uso atualizado
if __name__ == "__main__":
    db = SingleStoreMed()
    
    # Simulação: Decision Tree retornou Cardiology (ID 1)
    result = db.get_medical_info(
        specialty_id=1,
        user_query="dor no peito e falta de ar"
    )
    
    print("═"*50)
    print("💡 Informação Relevante:")
    for info in result['relevant_info']:
        print(f"\n📄 {info['text'][:150]}... (Confiança: {info['confidence']})")
    
    print("\n🔗 Fontes Consultadas:")
    for source in result['sources']:
        print(f"  - {source}")
    
    print("\n⚠️ Recomendação:")
    print(result['recommendation'])