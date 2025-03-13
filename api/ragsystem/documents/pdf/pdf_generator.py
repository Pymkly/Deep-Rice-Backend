from config import RICE_PDF_TEMPLATE
from api.ragsystem.documents.main_process.generator.document_generator import DocumentGenerator


class PdfGenerator(DocumentGenerator):
    def __init__(self, template_path=RICE_PDF_TEMPLATE):
        super().__init__(template_path)
