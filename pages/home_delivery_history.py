import streamlit as st

import pandas as pd

from db import conn, cursor

cursor = conn.cursor()

st.title("🚚 Home Delivery History")

orders = cursor.execute("""
    SELECT delivery_id, customer_name, mobile_number,
           product_name, quantity, total_amount, order_date
    FROM home_delivery_orders
    ORDER BY order_date DESC
""").fetchall()

if not orders:
    st.info("No home delivery orders yet.")
else:
    df = pd.DataFrame(
        orders,
        columns=[
            "Delivery ID", "Customer Name", "Mobile",
            "Product", "Quantity", "Total Amount", "Date"
        ]
    )

    st.dataframe(df, use_container_width=True)
