from api.ragsystem.documents.images.image_generator import ImageGenerator
from api.ragsystem.documents.images.image_processor import ImageProcessor
from api.ragsystem.documents.images.image_retriever import ImageRetriever
from api.ragsystem.documents.main_process.handler.document_handler import DocumentHandler


class ImageHandler(DocumentHandler):
    def __init__(self, encoder):
        super().__init__(ImageProcessor(encoder), ImageRetriever(encoder), ImageGenerator())
