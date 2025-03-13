# Exemple : Extraction depuis un PDF
from api.ragsystem.textextraction.pdfextractor import extract_text_from_pdf

from api.utils.deepriceutils import get_pdf_files

pdf_text = extract_text_from_pdf('../rag-data/rice/disease/ID.pdf')
print(pdf_text)

files = get_pdf_files('../rag-data/rice/000040-disease/')
print(files)