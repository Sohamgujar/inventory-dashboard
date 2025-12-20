import streamlit as st
import pandas as pd
from db import conn, cursor
import io

st.title("📋 Inventory List")

# Fetch products from Supabase
cursor.execute("""
    SELECT product_id, name, category, cost_price, selling_price, quantity
    FROM products
    ORDER BY product_id
""")

rows = cursor.fetchall()

if not rows:
    st.info("Inventory is empty.")
else:
    df = pd.DataFrame(
        rows,
        columns=[
            "Product ID",
            "Name",
            "Category",
            "Cost Price",
            "Selling Price",
            "Quantity"
        ]
    )

    st.dataframe(df, use_container_width=True)

    # Download as Excel
    def to_excel(dataframe):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            dataframe.to_excel(writer, index=False, sheet_name="Inventory")
        return output.getvalue()

    excel_data = to_excel(df)

    st.download_button(
        label="📥 Download Inventory as Excel",
        data=excel_data,
        file_name="inventory.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
