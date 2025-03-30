import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from dotenv import load_dotenv
import singlestoredb as s2
import os

load_dotenv()

def get_gemini_model(model_name="gemini-2.0-flash"):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    return genai.GenerativeModel(model_name)

def generate_embedding(texto):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    try:
        embedding = model.encode(texto)
        embedding = np.round(embedding, 6).tolist()
    except Exception as e:
        print(f"Erro ao processar informação: {e}")
        embedding = None
    return embedding

def search_relevant_articles(prompt):

    question_embedding = generate_embedding(prompt)
    if question_embedding is None:
        return None  
    
    cursor.execute("""
        SELECT pdf_embeddings.id, pdf_embeddings.document_id, pdf_embeddings.embedding, documentos_pdf.texto_extraido 
        FROM pdf_embeddings
        JOIN documentos_pdf ON pdf_embeddings.document_id = documentos_pdf.id
    """)
    artigos = cursor.fetchall()

    embeddings_com_similaridade = []
    for id, document_id, emb_blob, conteudo in artigos:
        try:

            embedding_article = np.frombuffer(emb_blob, dtype=np.float32).reshape(1, -1)  
            similarity = cosine_similarity([question_embedding], embedding_article)[0][0]  
            embeddings_com_similaridade.append((similarity,document_id, conteudo, id))  
        except Exception as e:
            print(f"Erro ao processar embedding do artigo {id}: {e}")

    embeddings_com_similaridade.sort(reverse=True, key=lambda x: x[0])  

    top_10_artigos = embeddings_com_similaridade[:10]
    return top_10_artigos

model = get_gemini_model()

conn = s2.connect(
    host='svc-2bb855a2-bafe-4117-b888-641a3ff41420-dml.aws-oregon-4.svc.singlestore.com',
    port=3306,
    user='admin',
    password='CVjXTlvNtj2mR4LjDtG6r1OwRwrmdAnq',
    database='db_smartnurse'
)

cursor = conn.cursor()

context = """
Você é um assistente médico altamente qualificado. Responda às perguntas com base em evidências científicas, 
de forma clara e objetiva. Evite suposições e forneça recomendações sempre que possível. Atenção queremos que a informação seja entregue
de forma simples, clara mas correta, visto ter o propósito de aprendizagem. Tudo o que seja fora da área
medicinal não deverá ser respondido. É preferível reconhecer que não tens informação para responder
do que entregar informação errada que possa comprometer a saúde do utilizador. Caso seja uma informação simples mas que não é a tua especialidade deves afirmar isso mesmo
lembra-te de ser educado, cumprimentar, e agradecer! Não é necessário informares ao utilizador a quais ficheiros tens acesso/foste buscar a informação a não ser que
seja especificamente pedido, ou seja coerente para explicar a informação. 
Podes utilizar emojis mas sem exagero.

Atenção! UTILIZA UNICA E EXCLUSIVAMENTE OS SEGUINTES DOCUMENTOS: {articles}

Pergunta: {pergunta}
"""

while True:
    prompt = input("Digite seu prompt (ou 'sair' para encerrar): ")

    if prompt.lower() == "sair":
        print("Chat encerrado.")
        break

    top10Articles = search_relevant_articles(prompt)

    if not top10Articles:
        # print("\nTop 10 artigos mais relevantes:")
        # for similarity, titulo, conteudo, id in top10Articles:
        #     print(f"\nID: {id}, Similaridade: {similarity:.4f}")
        #     print(f"Título: {titulo}")
        #     print(f"Conteúdo: {conteudo[:200]}...")  
    # else:
        print("Nenhum artigo relevante encontrado.")

    response = model.generate_content(context.format(articles=top10Articles, pergunta=prompt))
    print(response.text)

# finalArticles = "\n\n".join([f"Artigo {i+1}:\nTítulo: {titulo}\nConteúdo: {conteudo[:1000]}..." for i, (_, titulo, conteudo, _) in enumerate(articles)])