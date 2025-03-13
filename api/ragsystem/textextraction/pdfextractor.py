import pdfplumber
import re

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
        text = clean_text(text)
        return text

## extrait le contenu d'un pdf et assembler dans une seule variable
def extract_content_concat_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        content = ''
        mean_page = 0
        for page in pdf.pages:
            text = page.extract_text(layout=True)
            if text:
                text = clean_text(text)
                content += text + "\n\n"
                mean_page += len(text)
        mean_page = mean_page / len(pdf.pages)
        return (content, mean_page)

def extract_content_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        content = []
        for page in pdf.pages:
            text = page.extract_text()
            text = clean_text(text)
            content.append(text)
        return content

def clean_text(text):
    text = text.replace("\n\n", "[PARAGRAPH]")  # Marquer les paragraphes
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)  # Supprimer les césures de mots
    text = ' '.join(text.split())  # Supprimer les espaces multiples
    text = text.replace("[PARAGRAPH]", "\n\n")  # Restaurer les paragraphes
    # 🔴 Supprimer les longues lignes de "." et autres motifs inutiles
    text = re.sub(r'\.{3,}', '.', text)  # Supprime toute suite de 5 points ou plus
    text = re.sub(r'_{3,}', '_', text)  # Supprime toute suite de 5 underscores ou plus
    text = re.sub(r'-{3,}', '-', text)  # Supprime toute suite de 5 tirets ou plus
    return text