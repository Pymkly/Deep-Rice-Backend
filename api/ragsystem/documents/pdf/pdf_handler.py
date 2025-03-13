from api.ragsystem.documents.main_process.handler.document_handler import DocumentHandler
from api.ragsystem.documents.pdf.pdf_processor import PDFProcessor
from api.ragsystem.documents.pdf.pdf_generator import PdfGenerator
from api.ragsystem.documents.pdf.pdf_retriever import PDFRetriever


class PDFHandler(DocumentHandler):
    def __init__(self, encoder):
        super().__init__(PDFProcessor(encoder), PDFRetriever(encoder, top_k=30), PdfGenerator())
