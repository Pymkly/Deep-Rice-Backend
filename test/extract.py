from ragsystem.textextraction.pdfextractor import extract_content_from_pdf

path = "../rag-data/rice/disease/1698-Article Text-1897-1-10-20170727.pdf"

result = extract_content_from_pdf(path)
print(len(result))
for r in result:
    print(r)