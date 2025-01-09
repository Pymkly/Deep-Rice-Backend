import pdfplumber

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
        text = clean_text(text)
        return text

def clean_text(text):
    text = text.replace('\n', ' ')  # Supprime les retours à la ligne
    text = ' '.join(text.split())  # Supprime les espaces multiples
    return text
