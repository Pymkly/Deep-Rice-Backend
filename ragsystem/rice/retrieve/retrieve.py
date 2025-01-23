from sklearn.metrics.pairwise import cosine_similarity

from api.database.conn import get_mongo_db
from ragsystem.rice.collect.ricepdfextractor import model
import numpy as np

def relevant_info(query, max_threshold=0.):
    documents = find_all()
    query_embedded = model.encode([query])
    similarities = []
    relevant_documents = [document for document in documents if similarity(query_embedded, document, similarities) >= max_threshold]
    return relevant_documents, similarities

def similarity(query_embedded, document, similarities=None):
    if similarities is None:
        similarities = []
    document_embedded = np.array(document['key'])
    result = cosine_similarity(query_embedded, [document_embedded])
    similarities.append(result)
    return result

def find_all():
    db = get_mongo_db()
    collection = db["rice_pdf_documents"]
    return collection.find()
