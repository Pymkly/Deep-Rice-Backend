import pickle
import os
import warnings

import psycopg2
import tensorflow as tf
import numpy as np

from config import ROOT_DIR, DB_PATH
from tensorflow.keras.applications.resnet50 import preprocess_input

# project root


_root = "./data"
train_directory = f"{_root}/train"
val_directory = f"{_root}/val"
test_directory = f"{_root}/test"
IMG_SIZE = (224,224)
BATCH = 32


DB_PATH = os.path.join(ROOT_DIR, os.path.normpath(DB_PATH))

def get_classes_db_without_cursor(_index):
    from api.database.conn import get_conn
    conn = None
    cursor = None
    try:
        conn = get_conn()
        cursor = conn.cursor()
        label_, disease_, diseases_ = get_classes_db(cursor, _index)
    except psycopg2.Error as e:
        print("Erreur lors de la connexion ou de la requête :", e)
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return label_, disease_, diseases_

def get_classes_db(cursor, _index):
    from api.disease.disease import get_all_diseases
    disease = get_all_diseases(cursor)
    return disease[_index]['name'], disease[_index], disease


def get_classes(_index):
    warnings.warn(
        "get_classes is deprecated and will be removed in a future version. Use get_classes_db or get_classes_db_without_cursor instead.",
        DeprecationWarning,
        stacklevel=2
    )
    _classes = ['Bacterialblight', 'Blast', 'Brownspot', 'Healthy Rice Leaf', 'Tungro']
    return _classes[_index]

def load_data():
    train_data = tf.keras.preprocessing.image_dataset_from_directory(
        directory=train_directory,
        image_size=IMG_SIZE,
        batch_size=BATCH,
        label_mode='categorical'
    )
    val_data = tf.keras.preprocessing.image_dataset_from_directory(
        directory=val_directory,
        image_size=IMG_SIZE,
        batch_size=BATCH,
        label_mode='categorical'
    )

    test_data = tf.keras.preprocessing.image_dataset_from_directory(
        directory=test_directory,
        image_size=IMG_SIZE,
        batch_size=BATCH,
        label_mode='categorical'
    )
    return train_data, val_data, test_data

def persist_model(model, path):
    print(f"Persisting the model to {path}")
    model_dir = os.path.dirname(path)
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    with open(path, "wb") as file:
        pickle.dump(model, file)
    print(f"Done")

def load_model(path):
    print(f"Loading the model from {path}")
    with open(path, "rb") as file:
        model = pickle.load(file)
    print(f"Done")
    return model


def preprocess_image_for_prediction(image_path, img_size=IMG_SIZE):
    """
    Prépare une image pour la prédiction, en la redimensionnant et en la normalisant.

    :param image_path: Chemin de l'image à prédire.
    :param img_size: Taille de l'image attendue (comme défini dans `image_size`).
    :return: Image prétraitée sous forme de tenseur.
    """
    # Charger l'image depuis le fichier
    image = tf.keras.preprocessing.image.load_img(image_path, target_size=img_size)

    # Convertir l'image en tableau NumPy
    image_array = tf.keras.preprocessing.image.img_to_array(image)

    # Ajouter une dimension batch (1, height, width, channels)
    image_array = np.expand_dims(image_array, axis=0)

    # Normaliser les valeurs des pixels (similaire au traitement des datasets)
    # image_array = image_array / 255.0
    image_array = preprocess_input(image_array)
    return image_array