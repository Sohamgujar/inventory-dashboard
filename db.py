import psycopg2
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

conn = psycopg2.connect(
    DATABASE_URL,
    sslmode="require"
)

conn.autocommit = False
cursor = conn.cursor()

def reset_transaction():
    try:
        conn.rollback()
    except:
        pass
