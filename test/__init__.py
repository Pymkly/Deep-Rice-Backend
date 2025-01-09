# Exemple : Extraction depuis un PDF
from ragsystem.textextraction.pdfextractor import extract_text_from_pdf

pdf_text = extract_text_from_pdf('../rag-data/rice/disease/ID.pdf')
print(pdf_text)