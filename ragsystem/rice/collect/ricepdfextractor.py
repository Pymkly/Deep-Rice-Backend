from sentence_transformers import SentenceTransformer
from api.database.conn import get_mongo_db
from api.utils.deepriceutils import get_pdf_files
from ragsystem.textextraction.pdfextractor import extract_text_from_pdf, extract_content_from_pdf
from config import RICE_RAG_PATH

model = SentenceTransformer('all-mpnet-base-v2')




def extract_save_mongo_all_rice_txt_pdf():
    db = get_mongo_db()
    collection = db["rice_pdf_documents"]
    documents = rice_content_pdf()
    for document in documents:
        collection.insert_one(document)
    print("Tous les documents ont été stockés dans MongoDB.")


def rice_content_pdf():
    pdf_items = extract_all_rice_content_pdf()
    documents = []
    for pdf, contents in pdf_items.items():
        for text in contents:
            key = model.encode([text])[0].tolist()
            document = {
                "filename": pdf,
                "content": text,
                "key": key,
                "metadata": {
                    "source": pdf,
                    "length": len(text.split())  # Nombre de mots
                }
            }
            documents.append(document)
    return documents

def extract_all_rice_txt_pdf():
    pdf_files = get_pdf_files(RICE_RAG_PATH)
    pdf_texts = {pdf: extract_text_from_pdf(pdf) for pdf in pdf_files}
    return pdf_texts


def extract_all_rice_content_pdf():
    pdf_files = get_pdf_files(RICE_RAG_PATH)
    pdf_texts = {pdf: extract_content_from_pdf(pdf) for pdf in pdf_files}
    return pdf_texts