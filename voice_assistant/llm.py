import os
import requests
from bs4 import BeautifulSoup
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Configuração da API OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

class WebDocument:
    def __init__(self, content, metadata=None):
        self.page_content = content
        self.metadata = metadata if metadata is not None else {}

def scrape_web_links(links):
    documents = []
    for link in links:
        try:
            response = requests.get(link)
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text(separator=' ')
            documents.append(WebDocument(text, {'source': link}))
            print(f"Conteúdo coletado do link: {link}")
        except Exception as e:
            print(f"Erro ao coletar o link {link}: {e}")
    return documents

def load_pdfs(pdf_directory):
    documents = []
    for filename in os.listdir(pdf_directory):
        if filename.endswith('.pdf'):
            filepath = os.path.join(pdf_directory, filename)
            loader = PyPDFLoader(filepath)
            documents.extend(loader.load())
            print(f"Carregado {len(loader.load())} documentos de {filename}")
    return documents

def load_and_index_content(pdf_directory, links):
    pdf_texts = load_pdfs(pdf_directory)
    web_texts = scrape_web_links(links)
    
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    
    pdf_chunks = text_splitter.split_documents(pdf_texts)
    web_chunks = text_splitter.split_documents(web_texts)
    
    pdf_index = FAISS.from_documents(pdf_chunks, embeddings)
    web_index = FAISS.from_documents(web_chunks, embeddings)
    
    return pdf_index, web_index

def query_knowledge_base(query, pdf_index, web_index, prompt, history=[]):
    pdf_docs = pdf_index.similarity_search(query, k=3)
    web_docs = web_index.similarity_search(query, k=3)
    
    combined_docs = pdf_docs + web_docs
    if not combined_docs:
        return "Desculpe, mas os documentos fornecidos não contêm informações sobre a consulta."
    
    combined_content = " ".join([doc.page_content for doc in combined_docs])
    
    history.append({"role": "user", "content": f"Documentos:\n{combined_content}\n\nConsulta: {query}"})
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt}] + history,
        max_tokens=900,
        temperature=0,
        n=1,
        stop=None
    )
    
    reply = response.choices[0].message.content.strip()
    history.append({"role": "assistant", "content": reply})
    return reply

"""
pdf_directory = os.path.join(os.path.dirname(__file__), 'pdfs')
pdf_index, web_index = load_and_index_content(pdf_directory, ['https://www.google.com/'])
history = []
query = "Quais são as diretrizes de identidade visual da Tahto?"
prompt = "Responda com base nos documentos fornecidos."

response = query_knowledge_base(query, pdf_index, web_index, prompt, history)
print(response)
"""
