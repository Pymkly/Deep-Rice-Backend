import psycopg2

from api.database.conn import get_conn


def get_all_diseases_without_cursor():
    conn = None
    cursor = None
    try:
        conn = get_conn()
        cursor = conn.cursor()
        diseases = get_all_diseases(cursor)
    except psycopg2.Error as e:
        print("Erreur lors de la connexion ou de la requête :", e)
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return diseases

def get_all_diseases(cursor):
    query = """
            SELECT id, name, description, instructions
            FROM diseases
            ORDER BY name ASC;
            """
    cursor.execute(query)
    rows = cursor.fetchall()

    # Transformer les résultats en liste de dictionnaires
    diseases = [
        {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "instructions": row[3]
        }
        for row in rows
    ]
    return diseases