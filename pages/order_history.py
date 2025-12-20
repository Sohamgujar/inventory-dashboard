import streamlit as st
import sqlite3
import pandas as pd

# DB connection
conn = sqlite3.connect("inventory.db", check_same_thread=False)
cursor = conn.cursor()

st.title("📜 Order History")

# Fetch all orders
orders = cursor.execute("""
    SELECT order_id, order_date, total_amount
    FROM orders
    ORDER BY order_date DESC
""").fetchall()

if not orders:
    st.info("No orders found.")
else:
    orders_df = pd.DataFrame(
        orders,
        columns=["Order ID", "Date & Time", "Total Amount"]
    )

    st.subheader("🧾 All Orders")
    st.dataframe(orders_df, use_container_width=True)

    st.divider()

    # Select order to view details
    order_ids = orders_df["Order ID"].tolist()
    selected_order = st.selectbox("Select Order ID to view details", order_ids)

    if selected_order:
        items = cursor.execute("""
            SELECT p.name, oi.quantity, oi.price
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = ?
        """, (selected_order,)).fetchall()

        if items:
            items_df = pd.DataFrame(
                items,
                columns=["Product Name", "Quantity", "Price (Per Item)"]
            )
            items_df["Total"] = items_df["Quantity"] * items_df["Price (Per Item)"]

            st.subheader(f"📦 Order #{selected_order} Details")
            st.dataframe(items_df, use_container_width=True)

            st.markdown(
                f"### 💰 Order Total: ₹ {items_df['Total'].sum()}"
            )

    # ================= ADDITIONS START HERE =================

    st.divider()

    # -------- TOTAL INCOME --------
    st.subheader("💰 Total Income")

    total_income = orders_df["Total Amount"].sum()
    st.markdown(f"## ₹ {total_income}")

    st.divider()

    # -------- DAY-WISE SALES --------
    st.subheader("📅 Day-wise Sales")

    orders_df["Date"] = pd.to_datetime(
        orders_df["Date & Time"]
    ).dt.date

    day_wise_sales = (
        orders_df
        .groupby("Date")["Total Amount"]
        .sum()
        .reset_index()
    )

    day_wise_sales.columns = ["Date", "Total Sales"]

    st.dataframe(day_wise_sales, use_container_width=True)
