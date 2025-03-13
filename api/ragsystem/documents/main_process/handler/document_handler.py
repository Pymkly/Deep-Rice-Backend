import os

from api.ragsystem.documents.main_process.generator.document_generator import DocumentGenerator
from api.ragsystem.documents.main_process.processor.document_processor import DocumentProcessor
from api.ragsystem.documents.main_process.retriever.document_retriever import Retriever
from api.utils.deepriceutils import get_file_extension_category, get_file_extension


class DocumentHandler:
    def __init__(self, processor:DocumentProcessor, retriever:Retriever, generator:DocumentGenerator):
        self.processor = processor
        self.retriever = retriever
        self.generator = generator

    def key(self):
        # extension est déja la catégorie     00
        return self.processor.extension.lower()

    def can_handle_file(self, file_path):
        """Vérifie si le handler peut gérer ce fichier en fonction de son extension."""
        ext = get_file_extension(file_path)
        category = get_file_extension_category(ext)
        return category == self.processor.extension.lower()

    def process_documents(self):
        """Extrait et stocke les documents dans la base"""
        self.processor.save_documents_postgres_wcon()

    def retrieve(self, query, cur):
        """Récupère les chunks pertinents pour une requête"""
        return self.retriever.retrieve(query, cur)

    def generate_prompt(self, retrieved_chunks):
        """Génère une réponse basée sur les chunks récupérés"""
        return self.generator.generate_prompt(retrieved_chunks)

    def process_file(self, cur, file_path):
        """Enregistre un fichier, l’analyse et l’ajoute à la base."""
        if not self.can_handle_file(file_path):
            raise ValueError(f"Ce handler ne peut pas traiter le fichier : {file_path}")
        save_path = self.processor.get_absolute_folder()

        # Sauvegarder le fichier sur disque
        os.makedirs(save_path, exist_ok=True)
        file_name = os.path.basename(file_path)
        new_file_path = os.path.join(save_path, file_name)
        os.rename(file_path, new_file_path)

        # Enregistrer les contenus et embeddings dans la base
        self.processor.save_document(cur, file_name)
        print(f"✅ Fichier {file_name} traité et stocké.")