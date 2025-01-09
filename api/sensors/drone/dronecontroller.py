from datetime import date
from typing import List

import psycopg2
from fastapi import UploadFile, File

import common
from api.database.conn import get_conn
from api.predict import predict_disease
from api.sensors.drone.dronereport import save_report, save_drone_image
from api.utils.deepriceutils import upload_images
from api.metadata.metadata import read_gps_coordinates
from api.lands.lands import get_parcels_contains_point

async def upload_drone_image(files: List[UploadFile] = File(...)):
    conn = None
    cursor = None
    try:
        conn = get_conn()
        cursor = conn.cursor()
        file_locations = await upload_images(files)
        drone_images = []
        for file_location in file_locations:
            drone_image = process_drone_image(cursor, file_location)
            drone_images.append(drone_image)
        today = date.today()
        _id = save_report(today, 'petite description', cursor)
        save_drone_images(drone_images, _id, cursor)
        conn.commit()
    except psycopg2.Error as e:
        print("Erreur lors de la connexion ou de la requête :", e)
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return {
        'predictions' : drone_images
    }

def save_drone_images(_drone_images, _id, cursor):
    for _drone_image in _drone_images:
        save_drone_image(_drone_image, _id, cursor)


def process_drone_image(cursor, file_location):
    lat, lon = read_gps_coordinates(file_location)
    parcels = get_parcels_contains_point(cursor, lat, lon)
    if len(parcels) == 0:
        raise Exception("No parcels found")
    parcel = parcels[0]
    predicted_class, probabilities = predict_disease(file_location)
    # label_ = common.get_classes(int(predicted_class))
    label_, disease_, diseases_ = common.get_classes_db_without_cursor(int(predicted_class))
    return {
        'parcel': parcel,
        'predicted_class': int(predicted_class),
        'predicted_class_': disease_,
        'label_': label_,
        'probability': float(probabilities[int(predicted_class)]),
        'longitude': lon,
        'latitude': lat,
        'photo_url': file_location
    }