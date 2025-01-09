import psycopg2

import common
from config import *


def get_conn():
    return psycopg2.connect(
        host=HOST,
        database=DATABASE,
        user=USER,
        password=PASSWORD
    )