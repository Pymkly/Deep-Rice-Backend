# from langchain.chains import RetrievalQA
# from langchain.llms import OpenAI

from ragsystem.rice.retrieve.document_search import search_documents
from transformers import pipeline

qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

# # Modèle génératif
# llm = OpenAI(model="text-davinci-003")  # Ou tout autre modèle supporté par LangChain
#
# # Fonction pour combiner recherche et génération
# def generate_answer(question, db):
#     documents = search_documents(question, db)
#     context = "\n".join(documents)
#     prompt = f"Voici des informations contextuelles :\n{context}\n\nQuestion : {question}\nRéponse :"
#     return llm(prompt)


def generate_answer(question, db):
    documents = search_documents(question, db)
    context = "\n".join(documents)
    # prompt = f"Voici des informations contextuelles :\n{context}\n\nQuestion : {question}\nRéponse :"
    response = qa_pipeline({"question":question, "context":context})
    return response