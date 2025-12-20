import streamlit as st

import pandas as pd

# Database connection
from db import conn, cursor

cursor = conn.cursor()

st.title("✏️ Manage Inventory (Edit / Delete)")

# Load products
products = cursor.execute("""
    SELECT product_id, name, category, cost_price, selling_price, quantity
    FROM products
""").fetchall()

if not products:
    st.info("No products available.")
    st.stop()

df = pd.DataFrame(
    products,
    columns=[
        "Product ID", "Name", "Category",
        "Cost Price", "Selling Price", "Quantity"
    ]
)

st.subheader("📋 Current Inventory")
st.dataframe(df, use_container_width=True)

st.divider()

# Select product
product_ids = df["Product ID"].tolist()
selected_id = st.selectbox("Select Product ID", product_ids)

product = df[df["Product ID"] == selected_id].iloc[0]

# Edit form
with st.form("edit_product"):
    name = st.text_input("Product Name", product["Name"])
    category = st.text_input("Category", product["Category"])
    cost_price = st.number_input(
        "Cost Price", value=float(product["Cost Price"]), step=0.1
    )
    selling_price = st.number_input(
        "Selling Price", value=float(product["Selling Price"]), step=0.1
    )
    quantity = st.number_input(
        "Quantity", value=int(product["Quantity"]), step=1
    )

    update_btn = st.form_submit_button("✅ Update Product")

if update_btn:
    cursor.execute("""
        UPDATE products
        SET name=?, category=?, cost_price=?, selling_price=?, quantity=?
        WHERE product_id=?
    """, (
        name, category, cost_price,
        selling_price, quantity, selected_id
    ))
    conn.commit()
    st.success("Product updated successfully 🔄")
    st.rerun()

st.divider()

# Delete product
st.subheader("🗑️ Delete Product")

delete_confirm = st.checkbox(
    "I understand this will permanently delete the product"
)

if delete_confirm:
    if st.button("❌ Delete Product"):
        cursor.execute(
            "DELETE FROM products WHERE product_id=?",
            (selected_id,)
        )
        conn.commit()
        st.success("Product deleted successfully 🗑️")
        st.rerun()

