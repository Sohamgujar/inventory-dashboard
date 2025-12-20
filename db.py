import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

import psycopg2
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

conn = psycopg2.connect(
    DATABASE_URL,
    sslmode="require"
)

conn.autocommit = False
cursor = conn.cursor()

# 🔑 FIX: Force schema
cursor.execute("SET search_path TO public;")
conn.commit()

def reset_transaction():
    try:
        conn.rollback()
    except:
        pass

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
