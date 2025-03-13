from sentence_transformers import SentenceTransformer

from api.ragsystem.documents.pdf.pdf_processor import PDFProcessor

encoder = SentenceTransformer('all-mpnet-base-v2')
pdf_processor = PDFProcessor(encoder)
pdf_processor.save_documents_postgres_wcon()
# csv_processor = CSVProcessor(encoder=encoder)
# csv_processor.save_documents_postgres_wcon()
