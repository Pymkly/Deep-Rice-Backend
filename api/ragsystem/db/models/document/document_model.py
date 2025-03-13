from api.database.conn import get_conn
from api.utils.deepriceutils import vector_to_str


def save_document(text, embedding, type_document='pdf'):
    conn = get_conn()
    cur = conn.cursor()
    save_document_wcon(text, embedding, cur, type_document=type_document)
    conn.commit()
    cur.close()
    conn.close()

def save_document_wcon(text, embedding, cur, type_document='pdf'):
    embedding_str = vector_to_str(embedding)
    # Vérifier si le document existe déjà
    cur.execute(
        "SELECT COUNT(*) FROM documents WHERE content = %s;", (text,)
    )
    if cur.fetchone()[0] > 0:
        print(f"⚠️ Chunk déjà présent, non inséré : {text[:50]}...")  # Affiche les 50 premiers caractères
        return
    # Insérer si ce n'est pas un doublon
    cur.execute(
        "INSERT INTO documents (content, embedding, type_document) VALUES (%s, %s::vector, %s)",
        (text, embedding_str, type_document)
    )
    print(f"Chunks indexés dans postgresql ✅")