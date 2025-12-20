import streamlit as st
import psycopg2

st.write("🔍 Secrets available:", st.secrets)

DATABASE_URL = st.secrets.get("DATABASE_URL", None)

st.write("🔗 DATABASE_URL value:", DATABASE_URL)

if DATABASE_URL is None:
    st.error("❌ DATABASE_URL not found in secrets")
    st.stop()

conn = psycopg2.connect(
    DATABASE_URL,
    sslmode="require"
)

cursor = conn.cursor()

def reset_transaction():
    try:
        conn.rollback()
    except:
        pass
