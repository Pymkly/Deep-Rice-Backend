from api.ragsystem.documents.main_process.retriever.document_retriever import Retriever
from config import PDF_EXTENSION


class PDFRetriever(Retriever):
    def __init__(self, encoder, top_k=5):
        super().__init__( encoder=encoder, top_k=top_k, type_document=PDF_EXTENSION)