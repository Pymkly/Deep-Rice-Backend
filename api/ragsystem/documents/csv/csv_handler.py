from api.ragsystem.documents.csv.csv_processor import CSVProcessor
from api.ragsystem.documents.csv.csv_generator import CSVGenerator
from api.ragsystem.documents.csv.csv_retriever import CSVRetriever
from api.ragsystem.documents.main_process.handler.document_handler import DocumentHandler


class CSVHandler(DocumentHandler):
    def __init__(self, encoder):
        super().__init__(CSVProcessor(encoder), CSVRetriever(encoder), CSVGenerator())
