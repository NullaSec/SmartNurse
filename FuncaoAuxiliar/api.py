import json  # Adicionar essa importação
import numpy as np
import singlestoredb as s2
import fitz  # PyMuPDF para extrair texto do PDF
from sentence_transformers import SentenceTransformer

# Conectar ao banco de dados SingleStore
conexao = s2.connect(
    host='svc-2bb855a2-bafe-4117-b888-641a3ff41420-dml.aws-oregon-4.svc.singlestore.com',
    port=3306,
    user='admin',
    password='CVjXTlvNtj2mR4LjDtG6r1OwRwrmdAnq',
    database='db_smartnurse'
)

# Carregar modelo de embeddings
modelo = SentenceTransformer('all-MiniLM-L6-v2')

# Caminho do PDF
caminho_pdf = 'Files/Geral/file27.pdf'

try:
    # 1️⃣ Abrir o PDF e extrair o texto
    with open(caminho_pdf, 'rb') as file:
        conteudo_pdf = file.read()

    # Extrair texto do PDF
    with fitz.open(stream=conteudo_pdf, filetype="pdf") as doc:
        texto_extraido = "\n".join([pagina.get_text() for pagina in doc])

    # 2️⃣ Inserir o PDF e texto no banco
    cursor = conexao.cursor()
    print(f"Inserindo o arquivo '{caminho_pdf}' no banco...")
    
    query = "INSERT INTO documentos_pdf (nome_arquivo, conteudo, texto_extraido, especialidade_id) VALUES (%s, %s, %s, %s)"
    valores = (caminho_pdf, conteudo_pdf, texto_extraido, 8)
    cursor.execute(query, valores)
    conexao.commit()

    # 3️⃣ Obter ID do documento recém-adicionado
    documento_id = cursor.lastrowid

    if documento_id is None or documento_id <= 0:
        print(f"❌ Erro: documento_id inválido ({documento_id}).")
        exit()

    print(f"✅ PDF '{caminho_pdf}' inserido com ID {documento_id}!")

except Exception as e:
    print(f"❌ Erro ao inserir PDF no banco: {e}")
    exit()

# 4️⃣ Criar embedding do texto
try:
    embedding = modelo.encode(texto_extraido)
    embedding = np.round(embedding, 6).tolist()

    # Converter para JSON
    embedding_json = json.dumps(embedding)

    # 5️⃣ Inserir embedding no banco
    embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()
    query = "INSERT INTO pdf_embeddings (document_id, embedding) VALUES (%s, %s)"
    cursor.execute(query, (documento_id, embedding_bytes))
    conexao.commit()
    print(f"✅ Embedding do PDF '{caminho_pdf}' salvo com sucesso!")

except Exception as e:
    print(f"❌ Erro ao inserir embedding: {e}")

finally:
    # 6️⃣ Fechar conexão
    cursor.close()
    conexao.close()
    print("🔒 Conexão fechada.")