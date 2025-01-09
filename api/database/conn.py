import psycopg2

import common


def get_conn():
    return psycopg2.connect(
        host=common.HOST,
        database=common.DATABASE,
        user=common.USER,
        password=common.PASSWORD
    )