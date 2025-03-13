import os
from api.utils.deepriceutils import huggingface_api_token
from langchain_community.llms import HuggingFaceEndpoint
from config import PROMPT_TEMPLATE

os.environ["HUGGINGFACEHUB_API_TOKEN"] = huggingface_api_token()
llm =  HuggingFaceEndpoint(repo_id="mistralai/Mistral-Nemo-Instruct-2407")


def generate_response(query, retrieved_chunks):
    """
    Génère une réponse en utilisant un LLM basé sur les chunks récupérés.

    :param query: Question posée par l'utilisateur.
    :param retrieved_chunks: Liste des chunks les plus pertinents.
    :return: Réponse générée par le LLM.
    """
    with open(PROMPT_TEMPLATE, "r", encoding="utf-8") as f:
        template = f.read()
    # Construire le prompt
    context = "\n".join([f"{i + 1}. {chunk}" for i, chunk in enumerate(retrieved_chunks)])
    prompt = template.format(context=context, query=query)
    response = llm.predict(prompt)
    return response, prompt

