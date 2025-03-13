from api.ragsystem.documents.main_process.processor.document_processor import DocumentProcessor
from api.ragsystem.textextraction.pdfextractor import extract_content_concat_from_pdf
from config import PDF_EXTENSION


class PDFProcessor(DocumentProcessor):
    """ Classe spécifique pour traiter les PDF """

    def __init__(self, encoder):
        super().__init__(encoder, PDF_EXTENSION)

    def extract_content(self, pdf_file):
        _absolute_path = self.get_absolute_path(pdf_file)
        content, mean_page = extract_content_concat_from_pdf(_absolute_path)
        self.update_chunk_size(mean_page)
        return self.split_documents(content)

    def update_chunk_size(self, mean_page):
        self.chunk_size = mean_page
        self.chunk_overlay = mean_page*0.1

    def extract_contents(self):
        pdf_files = self.get_files_on_folder()
        pdf_texts = [extract_content_concat_from_pdf(pdf) for pdf in pdf_files]
        all_chunks = []
        for content, mean_page in pdf_texts:
            self.update_chunk_size(mean_page=mean_page)
            all_chunks.extend(self.split_documents(content))
        return all_chunks
