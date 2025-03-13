import chromadb


def get_chroma_collection(db_path="./chroma_db", collection_name="rag_chunks", delete=False):
    """
    Initialise la connexion à ChromaDB et retourne la collection spécifiée.

    :param delete:
    :param db_path: Chemin de stockage de la base ChromaDB (par défaut ./chroma_db)
    :param collection_name: Nom de la collection à récupérer ou créer
    :return: Objet collection ChromaDB
    """
    chroma_client = chromadb.PersistentClient(path=db_path)
    if delete:
        chroma_client.delete_collection(name=collection_name)
    collection = chroma_client.get_or_create_collection(name=collection_name)
    return collection
