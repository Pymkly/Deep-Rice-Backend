from api.ragsystem.documents.main_process.generator.document_generator import DocumentGenerator
from config import RICE_IMAGE_TEMPLATE


class ImageGenerator(DocumentGenerator):
    def __init__(self, template_path=RICE_IMAGE_TEMPLATE):
        super().__init__(template_path)
