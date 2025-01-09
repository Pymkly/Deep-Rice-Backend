import psycopg2

import common
from api.database.conn import get_conn
from api.disease.disease import get_all_diseases
from api.lands.lands import get_land_data, get_land_data_with_cursor
from api.utils.deepriceutils import readable_point

def get_drone_report_with_details_without_con(report_id):
    conn = None
    cursor = None
    try:
        conn = get_conn()
        cursor = conn.cursor()
        report = get_drone_report_with_details(report_id, cursor)
        land = get_land_data_with_cursor(1, cursor)
        response = {
            'report': report,
            'land': land
        }
    except psycopg2.Error as e:
        print("Erreur lors de la connexion ou de la requête :", e)
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return response

def get_drone_report_with_details(report_id, cursor):
    report_query = """
            SELECT id, report_date, description, created_at
            FROM drone_report
            WHERE id = %s;
            """
    cursor.execute(report_query, (report_id,))
    report = cursor.fetchone()
    if not report:
        return {"error": f"Drone report with ID {report_id} not found"}
    report_data = {
        "id": report[0],
        "report_date": report[1],
        "description": report[2],
        "created_at": report[3]
    }
    report_data["images"] = get_drone_image(cursor, report_id)
    return report_data

def get_drone_image(cursor, report_id):
    images_query = """
            SELECT id, photo_url, predicted_class, probability, ST_AsText(location) AS location, parcel_id, created_at
            FROM drone_images
            WHERE report_id = %s;
            """
    cursor.execute(images_query, (report_id,))
    images = cursor.fetchall()
    diseases_ = get_all_diseases(cursor)
    image_details = []
    for image in images:
        latitude, longitude = readable_point(image[4])
        image_details.append({
            "id": image[0],
            "photo_url": image[1],
            "predicted_class": image[2],
            "class": diseases_[int(image[2])]['name'],
            "class_": diseases_[int(image[2])],
            "probability": image[3],
            "location": {
                "longitude": longitude,
                "latitude": latitude
            },
            "parcel_id": image[5],
            "created_at": image[6]
        })
    return image_details

async def get_all_report_without_con():
    conn = None
    cursor = None
    try:
        conn = get_conn()
        cursor = conn.cursor()
        report = get_all_report(cursor)
    except psycopg2.Error as e:
        print("Erreur lors de la connexion ou de la requête :", e)
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return report

def get_all_report(cursor):
    report_query = """
            SELECT id, report_date, description, created_at
            FROM drone_report
            ORDER BY created_at DESC;
            """
    cursor.execute(report_query)
    return cursor.fetchall()

def save_report(report_date, description, cursor):
    report_query = """
            INSERT INTO drone_report (report_date, description)
            VALUES (%s, %s)
            RETURNING id;
            """
    cursor.execute(report_query, (report_date, description))
    report_id = cursor.fetchone()[0]
    return report_id

def save_drone_image(drone_image, report_id, cursor):
    image_query = """
            INSERT INTO drone_images (report_id, photo_url, predicted_class, location, parcel_id, probability)
            VALUES (%s, %s, %s, ST_SetSRID(ST_Point(%s, %s), 4326), %s, %s);
            """
    cursor.execute(image_query, (
        report_id,
        drone_image["photo_url"],
        drone_image["predicted_class"],
        drone_image["longitude"],
        drone_image["latitude"],
        drone_image["parcel"]['id'],
        drone_image["probability"]
    ))