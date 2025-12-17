import streamlit as st
import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect("inventory.db", check_same_thread=False)
cursor = conn.cursor()

st.title("📋 Inventory List")

# Fetch products
cursor.execute("SELECT product_id, name, category, cost_price, selling_price, quantity FROM products")
rows = cursor.fetchall()

# Convert to DataFrame
df = pd.DataFrame(rows, columns=["Product ID", "Name", "Category", "Cost Price", "Selling Price", "Quantity"])

# Display table
st.dataframe(df, use_container_width=True)

# Optional: export to Excel
def to_excel(df):
    import io
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Inventory')
    writer.close()
    processed_data = output.getvalue()
    return processed_data

excel_data = to_excel(df)
st.download_button(label='📥 Download Inventory as Excel', data=excel_data, file_name='inventory.xlsx')
