from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

from api.database.conn import get_conn
from api.utils.deepriceutils import get_pdf_files
from config import RICE_RAG_PATH
from ragsystem.rice.db.models.document.document_model import save_document_wcon
from ragsystem.textextraction.pdfextractor import extract_content_concat_from_pdf

encoder = SentenceTransformer('all-mpnet-base-v2')
# Charger un modèle d'encodage Hugging Face
# encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def index_rice_documents_postgres():
    conn = get_conn()
    cur = conn.cursor()
    index_rice_documents_postgres_wcon(cur)
    conn.commit()
    cur.close()
    conn.close()

def index_rice_documents_postgres_wcon(cur):
    """
        Encode et stocke les chunks dans ChromaDB.
    """
    documents = rice_content_concat_pdf()
    count = 1
    for chunks in documents:
        chunk_vectors = encoder.encode(chunks).tolist()
        for i, chunk in enumerate(chunks):
            save_document_wcon(chunk, chunk_vectors[i], cur)
        print(f"Chunks indexés dans postgresql ✅ : {str(count)}")
        count += 1

def index_rice_documents(collection):
    """
        Encode et stocke les chunks dans ChromaDB.
    """
    documents = rice_content_concat_pdf()
    count = 1
    for chunks in documents:
        chunk_vectors = encoder.encode(chunks).tolist()
        for i, chunk in enumerate(chunks):
            collection.add(
                ids=[f"chunk_{i}"],
                embeddings=[chunk_vectors[i]],
                metadatas=[{"source": "PDF_XYZ"}],  # Optionnel
                documents=[chunk]
            )
        print(f"Chunks indexés dans ChromaDB ✅ : {str(count)}")
        count += 1

## extrait le contenu des pdf sur le riz
## retourne un tableau de string des pdfs
def rice_content_concat_pdf():
    pdf_items = extract_all_rice_content_concat_pdf()
    documents = []
    for pdf, contents in pdf_items.items():
        text_split = split_documents(contents)
        documents.append(text_split)
    return documents

def split_documents(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,  # Taille d'un chunk
        chunk_overlap=100  # Chevauchement pour garder du contexte entre les chunks
    )
    chunks = splitter.split_text(text)
    return chunks

## extrait le contenu des pdf sur le riz
## retourne un tableau de string des pdfs
def extract_all_rice_content_concat_pdf():
    pdf_files = get_pdf_files(RICE_RAG_PATH)
    pdf_texts = {pdf: extract_content_concat_from_pdf(pdf) for pdf in pdf_files}
    return pdf_texts

