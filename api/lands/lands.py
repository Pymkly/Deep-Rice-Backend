import psycopg2

from api.database.conn import get_conn
from api.utils.deepriceutils import readable_point, readable_polygone

def get_land_data(land_id):
    conn = None
    cursor = None
    try:
        conn = get_conn()
        cursor = conn.cursor()
        get_land_data_with_cursor(land_id, cursor)
    except psycopg2.Error as e:
        print("Erreur lors de la connexion ou de la requête :", e)
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_land_data_with_cursor(land_id, cursor):
    query = """
                    SELECT 
                        title,
                        ST_AsText(global_location) AS location, -- Convertit le point en texte (WKT)
                        ST_AsText(boundary) AS boundary -- Convertit le polygone en texte (WKT)
                    FROM lands
                    WHERE id = %s;
                    """
    cursor.execute(query, (land_id,))
    result = cursor.fetchone()
    if result:
        title, location_wkt, boundary_wkt = result
        latitude, longitude = readable_point(location_wkt)
        polygon_points = readable_polygone(boundary_wkt)
        parcels = get_parcels_by_land_id(cursor, land_id)
        return {
            "title": title,
            "global_location": {"latitude": latitude, "longitude": longitude},
            "boundary": polygon_points,
            "parcels": parcels
        }
    else:
        print("Aucun terrain trouvé avec l'ID :", land_id)
        return None

def get_parcels_contains_point(cursor, lon, lat):
    parcels_query = """
        SELECT id, title,
                ST_AsText(boundary) AS boundary
            FROM parcels
            WHERE ST_Contains(
                boundary,
                ST_SetSRID(ST_Point(%s, %s), 4326)
            );
            """
    return get_parcels(cursor, parcels_query, (lon, lat))

def get_parcels_by_land_id(cursor, land_id):
    parcels_query = """
            SELECT id,
                title,
                ST_AsText(boundary) AS boundary -- Convertit le polygone en texte (WKT)
            FROM parcels
            WHERE land_id = %s;
            """
    return get_parcels(cursor, parcels_query, (land_id,))

def get_parcels(cursor, parcels_query, param):
    cursor.execute(parcels_query, param)
    parcels_results = cursor.fetchall()

    parcels = []
    for _id, parcel_title, parcel_boundary_wkt in parcels_results:
        parcel_boundary = readable_polygone(parcel_boundary_wkt)
        parcels.append({
            "id": _id,
            "title": parcel_title,
            "boundary": parcel_boundary
        })
    return parcels