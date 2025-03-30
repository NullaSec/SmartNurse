import numpy as np
from sentence_transformers import SentenceTransformer
import singlestoredb as s2
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional
import logging

load_dotenv()

# Configuração de logging
logging.basicConfig(
    filename='medical_diagnosis.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class MedicalDiagnosisEngine:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.conn_params = {
            'host': os.getenv('SINGLESTORE_HOST'),
            'port': int(os.getenv('SINGLESTORE_PORT', '3306')),
            'user': os.getenv('SINGLESTORE_USER'),
            'password': os.getenv('SINGLESTORE_PASSWORD'),
            'database': os.getenv('SINGLESTORE_DB')
        }
        self.specialty_mapping = {
            "Cardiology": 1,
            "Neurology": 2,
            # Adicione outras especialidades conforme necessário
        }

    def _get_connection(self):
        """Estabelece conexão com o SingleStore DB"""
        try:
            return s2.connect(**self.conn_params)
        except Exception as e:
            logging.error(f"Connection error: {str(e)}")
            raise

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Gera embeddings para o texto de entrada"""
        try:
            embedding = self.embedding_model.encode(text)
            return np.round(embedding, 6).tolist()
        except Exception as e:
            logging.error(f"Embedding generation failed: {str(e)}")
            return None

    def search_medical_documents(self, symptoms: str, specialty_id: Optional[int] = None) -> List[Dict]:
        """
        Busca documentos médicos relevantes para os sintomas
        
        Args:
            symptoms: Descrição dos sintomas do paciente
            specialty_id: ID da especialidade médica (opcional)
            
        Returns:
            Lista de documentos ordenados por relevância
        """
        query_embedding = self.generate_embedding(symptoms)
        if not query_embedding:
            return []

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Converter embedding para formato binário
                    embedding_bytes = bytes(np.array(query_embedding, dtype=np.float32).tobytes())
                    
                    base_query = """
                        SELECT 
                            d.id,
                            d.titulo,
                            d.texto_extraido,
                            DOT_PRODUCT(e.embedding, JSON_ARRAY_PACK(%s)) AS similarity
                        FROM documentos_pdf d
                        JOIN pdf_embeddings e ON d.id = e.document_id
                        WHERE 1=1
                    """
                    
                    params = [str(query_embedding)]
                    
                    if specialty_id:
                        base_query += " AND d.especialidade_id = %s"
                        params.append(specialty_id)
                    
                    base_query += " ORDER BY similarity DESC LIMIT 10"
                    
                    cursor.execute(base_query, params)
                    
                    return [{
                        'id': row[0],
                        'title': row[1],
                        'content': row[2],
                        'similarity': float(row[3])
                    } for row in cursor.fetchall()]
                    
        except Exception as e:
            logging.error(f"Database query failed: {str(e)}")
            return []

    def generate_diagnostic_report(self, symptoms: str) -> Dict:
        """
        Gera um relatório de diagnóstico baseado nos documentos médicos
        
        Args:
            symptoms: Descrição dos sintomas do paciente
            
        Returns:
            Dicionário contendo:
            - possible_diagnoses: Lista de diagnósticos possíveis
            - recommended_actions: Ações recomendadas
            - supporting_evidence: Trechos de documentos relevantes
            - confidence: Nível de confiança (0-1)
        """
        # Primeiro tenta identificar a especialidade mais relevante
        specialty_priority = self._identify_specialty(symptoms)
        
        results = {}
        
        # Busca primeiro na especialidade específica
        if specialty_priority:
            results = self.search_medical_documents(symptoms, specialty_priority['id'])
        
        # Se não encontrar resultados suficientes, faz busca geral
        if not results or len(results) < 3:
            general_results = self.search_medical_documents(symptoms)
            results.extend(general_results)
            results = sorted(results, key=lambda x: x['similarity'], reverse=True)[:10]
        
        if not results:
            return {
                'possible_diagnoses': [],
                'recommended_actions': ["Consultar um médico imediatamente"],
                'supporting_evidence': [],
                'confidence': 0.0
            }
        
        # Processa os resultados para gerar o relatório
        diagnoses = set()
        evidence = []
        total_similarity = sum(r['similarity'] for r in results)
        
        for doc in results[:5]:  # Limita aos 5 mais relevantes
            # Extrai possíveis diagnósticos do conteúdo (simplificado)
            content = doc['content'].lower()
            if "diagnóstico" in content:
                start = content.index("diagnóstico") + len("diagnóstico")
                end = content.find(".", start)
                diagnoses.add(content[start:end].strip().capitalize())
            
            evidence.append({
                'title': doc['title'],
                'excerpt': doc['content'][:300] + "...",
                'similarity': doc['similarity']
            })
        
        confidence = min(1.0, total_similarity / 5)  # Normaliza a confiança
        
        return {
            'possible_diagnoses': list(diagnoses)[:3],  # Limita a 3 diagnósticos
            'recommended_actions': self._generate_actions(symptoms, results),
            'supporting_evidence': evidence,
            'confidence': round(confidence, 2)
        }
    
    def _identify_specialty(self, symptoms: str) -> Optional[Dict]:
        """Identifica a especialidade médica mais relevante para os sintomas"""
        symptom_keywords = {
            "cardiaco": "Cardiology",
            "coração": "Cardiology",
            "peito": "Cardiology",
            "neurológico": "Neurology",
            "cabeça": "Neurology",
            # Adicione mais mapeamentos conforme necessário
        }
        
        symptoms_lower = symptoms.lower()
        for keyword, specialty in symptom_keywords.items():
            if keyword in symptoms_lower:
                return {
                    'name': specialty,
                    'id': self.specialty_mapping.get(specialty)
                }
        return None
    
    def _generate_actions(self, symptoms: str, documents: List[Dict]) -> List[str]:
        """Gera ações recomendadas baseadas nos documentos"""
        actions = set()
        
        # Ações genéricas baseadas em sintomas
        if "dor" in symptoms.lower():
            actions.add("Tomar analgésico conforme orientação médica")
        if "febre" in symptoms.lower():
            actions.add("Manter hidratação e monitorar temperatura")
        
        # Ações específicas dos documentos
        for doc in documents[:3]:
            content = doc['content'].lower()
            if "recomendação" in content:
                start = content.index("recomendação") + len("recomendação")
                end = content.find(".", start)
                recommendation = content[start:end].strip()
                if recommendation:
                    actions.add(recommendation.capitalize())
        
        if not actions:
            actions.add("Consultar um médico para avaliação")
        
        return list(actions)[:3]  # Limita a 3 ações

# Exemplo de uso
if __name__ == "__main__":
    engine = MedicalDiagnosisEngine()
    
    symptoms = input("Descreva seus sintomas: ")
    report = engine.generate_diagnostic_report(symptoms)
    
    print("\n🔍 Possíveis diagnósticos:")
    for diagnosis in report['possible_diagnoses']:
        print(f"- {diagnosis}")
    
    print("\n📌 Recomendações:")
    for action in report['recommended_actions']:
        print(f"- {action}")
    
    print(f"\n✅ Confiança: {report['confidence']*100}%")