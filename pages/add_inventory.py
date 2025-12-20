import streamlit as st
from db import conn, cursor

st.title("➕ Add Inventory")

with st.form("add_product_form"):
    name = st.text_input("Product Name")
    category = st.text_input("Category")
    cost_price = st.number_input("Cost Price", min_value=0.0, step=0.1)
    selling_price = st.number_input("Selling Price", min_value=0.0, step=0.1)
    quantity = st.number_input("Quantity", min_value=1, step=1)

    submit = st.form_submit_button("Add Product")

if submit:
    if name and category:
        cursor.execute("""
            INSERT INTO products
            (name, category, cost_price, selling_price, quantity)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING product_id
        """, (name, category, cost_price, selling_price, quantity))

        product_id = cursor.fetchone()[0]
        conn.commit()

        st.success(f"Product added successfully! Product ID: {product_id}")
    else:
        st.error("Please fill all fields")
