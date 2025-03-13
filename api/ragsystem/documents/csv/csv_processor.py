import csv

import pandas as pd

from api.ragsystem.documents.main_process.processor.document_processor import DocumentProcessor
from config import CSV_EXTENSION


class CSVProcessor(DocumentProcessor):
    """ Classe spécifique pour traiter les CSV """

    def __init__(self, encoder):
        super().__init__(encoder, extension=CSV_EXTENSION)
        self.chunk_size = 10

    def extract_content(self, csv_file):
        _absolute_path = self.get_absolute_path(csv_file)
        content = self.extract_content_from_file(_absolute_path)
        return self.split_documents(content)

    def extract_contents(self):
        csv_files = self.get_files_on_folder()
        csv_texts = {csv: self.extract_content_from_file(csv_file) for csv_file in csv_files}
        all_chunks = []
        for content in csv_texts.values():
            all_chunks.extend(self.split_documents(content))
        return all_chunks

    def split_documents(self, content):
        lines = content.split("\n")  # Diviser le CSV en lignes
        header = lines[0]  # Garder l'entête (les noms de colonnes)

        chunks = []
        for i in range(1, len(lines), self.chunk_size):  # Saut de `chunk_size` lignes
            chunk = "\n".join([header] + lines[i:i + self.chunk_size])  # Ajouter l'entête pour chaque chunk
            chunks.append(chunk)
        return chunks

    def extract_content_from_file(self, _file):
        """
            Lit un fichier CSV et convertit son contenu en texte structuré.

            :param _file: Chemin du fichier CSV
            :return: Chaîne de caractères contenant les données du CSV sous forme de texte
        """
        try:
            df = pd.read_csv(_file, dtype=str)
            # Vérifier si le fichier est vide
            if df.empty:
                return ""
            # Convertir chaque ligne du CSV en texte lisible, séparé par " | "
            sep = self.get_sep(_file)
            content = df.to_csv(index=False, sep=sep, lineterminator="\n")
            return content.strip()
        except Exception as e:
            print(f"Erreur lors de l'extraction du CSV {_file}: {e}")
            pass

    def get_sep(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            first_line = file.readline()
            detected_delimiter = csv.Sniffer().sniff(first_line).delimiter
            return detected_delimiter