from api.ragsystem.documents.main_process.retriever.document_retriever import Retriever
from config import CSV_EXTENSION


class CSVRetriever(Retriever):
    def __init__(self, encoder, top_k=5):
        super().__init__(encoder=encoder, top_k=top_k, type_document=CSV_EXTENSION)