# from flask import Flask, jsonify

# app = Flask(__name__)

# # Configuração da conexão com o banco de dados
# DB_CONFIG = {
#     "host": "svc-3482219c-a389-4079-b18b-d50662524e8a-shared-dml.aws-virginia-6.svc.singlestore.com",
#     "port": 3333,
#     "user": "guilherme",
#     "password": "JBpaDva5sr8SwuvZhNSEynlSOU8ftxSD",
#     "database": "db_smartnurse"
# }

# def query_db(query, args=(), one=False):
#     """Função auxiliar para executar queries no banco de dados."""
#     with s2.connect(**DB_CONFIG) as conn:
#         with conn.cursor() as cur:
#             cur.execute(query, args)
#             results = cur.fetchall()
#     return (results[0] if results else None) if one else results

# @app.route('/patients', methods=['GET'])
# def get_patients():
#     """Retorna os primeiros 5 pacientes."""
#     results = query_db("SELECT * FROM fake_patients_en ORDER BY id ASC LIMIT 5;")
    
#     patients_list = [
#         {
#             "Id": row[0], "name": row[1], "ssn": row[2], "age": row[3],
#             "dob": row[4], "address": row[5], "phone": row[6], "email": row[7],
#             "blood_type": row[8], "medical_condition": row[9], "medication": row[10],
#             "allergies": row[11], "condition_severity": row[12]
#         }
#         for row in results
#     ]
#     return jsonify(patients_list)

from flask import Flask, request, jsonify
from llm import PatientChatbot  # Importa a classe do seu arquivo
import logging

app = Flask(__name__)

# Configuração de logging
logging.basicConfig(level=logging.INFO)

# Inicializa o chatbot com o arquivo CSV dos pacientes
csv_path = "fake_patients_en.csv"
chatbot = PatientChatbot("fake_patients_en.csv")

@app.route("/ask_llm", methods=["POST"])
def ask_llm():
    """Recebe uma pergunta e retorna a resposta do LLM"""
    data = request.json
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "A pergunta não pode estar vazia"}), 400

    logging.info(f"Pergunta recebida: {question}")
    
    response = chatbot._ask_llm(question)
    return jsonify({"question": question, "response": response})

# Executa a API
if __name__ == "__main__":
    app.run(debug=True)
