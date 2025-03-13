from sklearn.metrics.pairwise import cosine_similarity

from api.utils.deepriceutils import vector_to_str
from ragsystem.rice.collect.db import get_chroma_collection
from ragsystem.rice.collect.ricepdfextractor import encoder as model

rag_collection = get_chroma_collection()

def relevant_info(query, cur, encoder=model, top_k=5):
    """
    Recherche les chunks les plus pertinents dans ChromaDB.

    :param query: Texte de la requête (question posée par l'utilisateur)
    :param cur: Curseur PostgreSQL
    :param encoder: Modèle d'encodage pour transformer la requête en vecteur
    :param top_k: Nombre de résultats à récupérer (par défaut 5)
    :return: Liste des documents retrouvés
    """
    query_vector = encoder.encode([query]).tolist()[0]  # Encoder la requête en vecteur
    query_vector_str = vector_to_str(query_vector)
    # Effectuer la recherche dans Postgresql
    cur.execute(
        """
        SELECT content, embedding <-> %s::vector AS distance
        FROM documents
        ORDER BY distance
        LIMIT %s;
        """,
        (query_vector_str, top_k)
    )

    # Récupérer les résultats
    results = cur.fetchall()
    chunks = [doc for doc, _ in results]
    return  chunks # Retourner les chunks retrouvés

def relevant_filtered_info(query, cur, encoder=model, top_k=5, threshold=0.5):
    retrieved_chunks = relevant_info(query, encoder=encoder, cur=cur, top_k=top_k)
    _count = len(retrieved_chunks)
    print(f"Nombre des chuncks : {_count}")
    query_vector = encoder.encode([query])[0]  # Encodage de la requête
    chunk_vectors = encoder.encode(retrieved_chunks)  # Encodage des chunks
    # Calcul de la similarité cosinus entre la requête et chaque chunk
    similarities = cosine_similarity([query_vector], chunk_vectors)[0]
    # Filtrer les chunks qui ont une similarité >= threshold
    filtered_chunks = [
        retrieved_chunks[i] for i in range(len(similarities)) if similarities[i] >= threshold
    ]
    return filtered_chunks