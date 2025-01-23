import pdfplumber
# from PyPDF2 import PdfReader
# from pdfminer.high_level import extract_text


# def find_title_from_text(file_path):
#     doc = fitz.open(file_path)
#     first_page = doc[0]
#
#     # Extraire le texte de la première page
#     text = first_page.get_text("text")
#     lines = text.split("\n")
#
#     # Filtrer pour trouver les lignes significatives
#     for line in lines:
#         stripped_line = line.strip()
#         if stripped_line and len(stripped_line) > 3:  # Éviter les lignes vides ou insignifiantes
#             return stripped_line
#     return "Titre introuvable dans le texte brut."

# def get_pdf_title(file_path):
#     # Extraire tout le texte
#     text = extract_text(file_path)
#     lines = text.split("\n")
#
#     # Retourner la première ligne non vide comme titre
#     for line in lines:
#         if line.strip():
#             return line.strip()
#     return "Titre introuvable"

# def get_pdf_title(file_path):
#     reader = PdfReader(file_path)
#
#     # Méta-données du PDF
#     metadata = reader.metadata
#     if metadata and metadata.title:
#         return metadata.title
#
#     # Si le titre n'est pas dans les méta-données, essayer d'extraire du contenu
#     first_page = reader.pages[0]
#     text = first_page.extract_text()
#     lines = text.split("\n")
#     return lines[0] if lines else "Titre introuvable"

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
        text = clean_text(text)
        return text

def extract_content_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        content = []
        for page in pdf.pages:
            text = page.extract_text()
            text = clean_text(text)
            content.append(text)
        return content

def clean_text(text):
    text = text.replace('\n', ' ')  # Supprime les retours à la ligne
    text = ' '.join(text.split())  # Supprime les espaces multiples
    return text
