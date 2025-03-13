from config import RICE_CSV_TEMPLATE
from api.ragsystem.documents.main_process.generator.document_generator import DocumentGenerator


class CSVGenerator(DocumentGenerator):
    def __init__(self, template_path=RICE_CSV_TEMPLATE):
        super().__init__(template_path)