from langchain.llms import HuggingFaceHub
import os
from api.utils.deepriceutils import huggingface_api_token
from langchain_community.llms import HuggingFaceEndpoint

os.environ["HUGGINGFACEHUB_API_TOKEN"] = huggingface_api_token()

llm =  HuggingFaceEndpoint(repo_id="mistralai/Mistral-Nemo-Instruct-2407")
out = llm.predict("Vous êtes expert en riziculture. Parlez du maladies piryculariose. Repondez en 5 phrases maximum.")
print(out)
