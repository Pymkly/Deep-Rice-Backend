import os
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

from langchain_text_splitters import RecursiveCharacterTextSplitter

from api.database.conn import get_conn
from api.utils.deepriceutils import get_file_extension_category, get_files_on_folder
from config import RICE_RAG_PATH, PDF_EXTENSION
from api.ragsystem.db.models.document.document_model import save_document_wcon


def save_embedded_document(cur, chunks, chunk_vectors, type_document='pdf'):
    for i, chunk in enumerate(chunks):
        save_document_wcon(chunk, chunk_vectors[i], cur, type_document=type_document)


class DocumentProcessor:
    def __init__(self, encoder, extension=PDF_EXTENSION):
        self.encoder = encoder
        self.chunk_size = 600
        self.chunk_overlay = 100
        ## change if it's not about rice
        self.base_path = RICE_RAG_PATH
        self.extension = extension

    def get_files_on_folder(self):
        return get_files_on_folder(self.base_path, self.extension)

    def get_absolute_path(self, file):
        abs_folder = self.get_absolute_folder()
        return os.path.join(abs_folder, file)

    def get_absolute_folder(self):
        sub_folder = get_file_extension_category(self.extension)
        return str(os.path.join(self.base_path, sub_folder))

    def extract_content(self, path):
        raise NotImplementedError("Implement this method to extract content from a document")

    def extract_contents(self):
        raise NotImplementedError("Implement this method to extract content from documents")

    def split_documents(self, text):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,  # Taille d'un chunk
            chunk_overlap=self.chunk_overlay  # Chevauchement pour garder du contexte entre les chunks
        )
        chunks = splitter.split_text(text)
        return chunks


    def encode_chunks(self, chunks):
        """ Encode les chunks en vecteurs """
        return self.encoder.encode(chunks).tolist()

    def encode_chunks_parallel(self, documents, num_threads=4):
        """Encode les chunks en parallèle avec ThreadPoolExecutor."""
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            chunks_vectors = [list(res) for res in executor.map(self.encode_chunks, documents)]
        # print("chunks_vectors")
        # print(chunks_vectors[0])
        return chunks_vectors

    def document_to_embedding(self, path):
        chunks = self.extract_content(path)
        chunk_vectors = self.encode_chunks(chunks)
        return chunks, chunk_vectors

    def save_document(self, cur, path):
        chunks, chunks_vector = self.document_to_embedding(path)
        save_embedded_document(cur, chunks, chunks_vector, type_document=self.extension)


    def documents_to_embedding(self):
        """
            Encode et stocke les chunks dans ChromaDB.
        """
        print("Start to extract content from documents")
        start = time.perf_counter()
        documents = self.extract_contents()
        print("Documents extracted, duration : {}".format(timedelta(seconds=time.perf_counter()-start)))
        print("Documents embedding started...")
        start = time.perf_counter()
        chunks_vectors = self.encode_chunks_parallel(documents, num_threads=10)
        print("Documents embedding finished... : {}".format(timedelta(seconds=time.perf_counter()-start)))
        ## document : [chunks], chunk_vectors: [[chunk_vector]]
        return documents, chunks_vectors

    def save_documents(self, cur):
        documents, chunks_vectors = self.documents_to_embedding()
        print("Start to save documents...")
        start = time.perf_counter()
        for i in range(len(documents)):
            chunk = documents[i]
            print(f"chunk {i}")
            save_document_wcon(chunk, chunks_vectors[i], cur, type_document=self.extension)
            # save_embedded_document(cur, chunks, chunks_vectors[i], type_document=self.extension)
        print("Done : {}".format(timedelta(seconds=time.perf_counter()-start)))

    def save_documents_postgres_wcon(self):
        conn = get_conn()
        cur = conn.cursor()
        self.save_documents(cur)
        conn.commit()
        cur.close()
        conn.close()