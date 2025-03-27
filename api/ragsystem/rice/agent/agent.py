import os

from sentence_transformers import SentenceTransformer

from api.ragsystem.documents.images.image_handler import ImageHandler
from api.utils.deepriceutils import huggingface_api_token, get_file_extension_category, get_file_extension
from config import PROMPT_TEMPLATE
from api.ragsystem.documents.csv.csv_handler import CSVHandler
from api.ragsystem.documents.main_process.generator.document_generator import DocumentGenerator
from api.ragsystem.documents.main_process.handler.document_handler import DocumentHandler
from api.ragsystem.documents.pdf.pdf_handler import PDFHandler
from langchain_community.llms import HuggingFaceEndpoint

os.environ["HUGGINGFACEHUB_API_TOKEN"] = huggingface_api_token()





class RiceAgent(DocumentGenerator):
    """
        Agent qui récupère automatiquement les informations depuis toutes les sources (PDF, CSV, DOCX...).
        Il utilise plusieurs retrievers et envoie les résultats au LLM.
        """

    def __init__(self):
        super().__init__(template_path=PROMPT_TEMPLATE)
        self.encoder = None
        self.llm = None
        self.handlers = None
        self.handlers_map = None
        self.refresh()

    def refresh(self):
        self.set_template(PROMPT_TEMPLATE)
        self.init_encoder()
        self.init_lln()
        self.init_handler()


    def init_handler(self):
        self.handlers = [PDFHandler(self.encoder), CSVHandler(self.encoder), ImageHandler(self.encoder)]
        self.handlers_map = {handler.key(): handler for handler in self.handlers}
        print(self.handlers_map)

    def get_handler_for_file(self, file_path) -> DocumentHandler:
        """Retourne le bon handler selon l'extension du fichier."""
        ext = get_file_extension(file_path)
        category = get_file_extension_category(ext)
        return self.handlers_map.get(category)

    def process_file(self, cur, file_path):
        """Enregistre et traite un fichier avec le bon handler."""
        handler = self.get_handler_for_file(file_path)
        if not handler:
            print(file_path)
            raise ValueError(f"Aucun handler ne prend en charge ce type de fichier : {file_path}")
        handler.process_file(cur, file_path)


    def init_lln(self):
        self.llm = HuggingFaceEndpoint(repo_id="mistralai/Mistral-Nemo-Instruct-2407")

    def init_encoder(self):
        self.encoder = SentenceTransformer('all-mpnet-base-v2', trust_remote_code=True)

    def save_documents(self):
        for handler in self.handlers:
            handler.process_documents()

    def ask(self, query, cur):
        """
                Recherche des informations sur le riz en interrogeant toutes les sources disponibles.

                :param query: Question posée par l'utilisateur
                :param cur: Curseur PostgreSQL pour la recherche
                :return: Réponse générée par le LLM + le prompt utilisé
                """
        context = ''
        # 🔍 **Parcourir chaque retriever pour récupérer les documents**
        for handler in self.handlers:
            # print(f"🔍 Recherche dans {retriever.__class__.__name__}...")
            chunks = handler.retrieve(query, cur)
            if len(chunks) > 0:
                context = f'{context}\n\n{handler.generate_prompt(chunks)}'
            # chunks.extend(retriever.retrieve(query, cur))  # Ajout des résultats au tableau
        # 📝 **Générer la requête**
        prompt_ = self.to_prompt_(query=query, context=context)
        # 📝 **Générer la réponse**
        print("📝 Génération de la réponse...")
        response = self.invoke_llm(prompt_)
        return response, prompt_

    def invoke_llm(self, prompt_):
        return self.llm.predict(prompt_)

    def to_prompt_(self, query, context ):
        return self.template.format(context=context, query=query)
