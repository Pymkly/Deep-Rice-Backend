from api.utils.deepriceutils import vector_to_str
from sklearn.metrics.pairwise import cosine_similarity

class Retriever:
    """
        Classe responsable de la recherche des documents les plus pertinents dans PostgreSQL.
        """

    def __init__(self, encoder, top_k=5, type_document='pdf'):
        """
        Initialise le retriever.

        :param encoder: Modèle d'encodage pour transformer les requêtes en vecteur
        :param top_k: Nombre de résultats à récupérer (par défaut 5)
        """
        self.encoder = encoder
        self.top_k = top_k
        self.threshold=0.5
        self.type_document=type_document

    def retrieve(self, query, cur):
        """
        Recherche les chunks les plus pertinents dans PostgreSQL.

        :param cur:
        :param query: Texte de la requête (question posée par l'utilisateur)
        :return: Liste des chunks retrouvés
        """
        query_vector = self.encoder.encode([query]).tolist()[0]  # Encoder la requête en vecteur
        query_vector_str = vector_to_str(query_vector)
        cur.execute(
            """
            SELECT content, embedding <-> %s::vector AS distance
            FROM documents
            WHERE type_document = %s
            ORDER BY distance
            LIMIT %s;
            """,
            (query_vector_str, self.type_document, self.top_k)
        )

        # Récupérer les résultats
        results = cur.fetchall()
        chunks = [doc for doc, _ in results]
        print("len(chunks)", len(chunks))
        return chunks

    def relevant_filtered_info(self, query, cur, encoder):
        retrieved_chunks = self.retrieve(query, cur=cur)
        _count = len(retrieved_chunks)
        print(f"Nombre des chuncks : {_count}")
        query_vector = encoder.encode([query])[0]  # Encodage de la requête
        chunk_vectors = encoder.encode(retrieved_chunks)  # Encodage des chunks
        # Calcul de la similarité cosinus entre la requête et chaque chunk
        similarities = cosine_similarity([query_vector], chunk_vectors)[0]
        # Filtrer les chunks qui ont une similarité >= threshold
        filtered_chunks = [
            retrieved_chunks[i] for i in range(len(similarities)) if similarities[i] >= self.threshold
        ]
        return filtered_chunks