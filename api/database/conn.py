import psycopg2
from pymongo import MongoClient
from config import MONGODB_DATABASE

import common
from config import *


def get_conn():
    return psycopg2.connect(
        host=HOST,
        database=DATABASE,
        user=USER,
        password=PASSWORD
    )

def get_mongo_db():
    client = MongoClient("mongodb://localhost:27017/")
    # Création d'une base et d'une collection
    db = client[MONGODB_DATABASE]
    return db