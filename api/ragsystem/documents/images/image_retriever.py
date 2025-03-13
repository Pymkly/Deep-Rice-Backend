from api.ragsystem.documents.main_process.retriever.document_retriever import Retriever
from config import IMAGE_EXTENSION


class ImageRetriever(Retriever):

    def __init__(self, encoder, top_k=5):
        super().__init__( encoder=encoder, top_k=top_k, type_document=IMAGE_EXTENSION)