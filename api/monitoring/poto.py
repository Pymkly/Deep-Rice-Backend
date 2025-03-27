from api.lands.lands import get_land_data_with_cursor
from api.utils.deepriceutils import readable_point

def get_poto(_poto_id, cursor):
    query = """
                SELECT 
                    title,
                    ST_AsText(global_location) AS location, -- Convertit le point en texte (WKT)
                    created_at,
                    id,
                    ref
                FROM potos
                WHERE id = %s
                """

    cursor.execute(query, (_poto_id,))
    result = cursor.fetchone()

    if result:
        title, location_wkt, created_at, id, ref = result
        latitude, longitude = readable_point(location_wkt)

        return {
            "id": id,
            "title": title,
            "location": {"latitude": latitude, "longitude": longitude},
            "created_at": created_at,
            "ref": ref
        }

    return None

def get_potos(_land_id, cursor):
    land = get_land_data_with_cursor(land_id=_land_id, cursor=cursor)
    potos = get_all_potos(cursor)
    param = {
        "potos" : potos,
        "land" : land
    }
    return param


def get_all_potos(cursor):
    query = """
            SELECT 
                title,
                ST_AsText(global_location) AS location, -- Convertit le point en texte (WKT)
                created_at,
                id,
                ref
            FROM potos
            """

    cursor.execute(query)
    results = cursor.fetchall()

    potos_list = []
    for result in results:
        title, location_wkt, created_at, id, ref = result
        latitude, longitude = readable_point(location_wkt)

        potos_list.append({
            "id": id,
            "title": title,
            "location": {"latitude": latitude, "longitude": longitude},
            "created_at": created_at,
            "ref": ref
        })

    return potos_list
