import streamlit as st
import sqlite3
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
from datetime import datetime

# DB connection
conn = sqlite3.connect("inventory.db", check_same_thread=False)
cursor = conn.cursor()

st.title("🛒 Checkout & Billing")

# Session cart
if "cart" not in st.session_state:
    st.session_state.cart = []

# Add product to cart
with st.form("add_to_cart"):
    product_id = st.number_input("Enter Product ID", min_value=1, step=1)
    qty = st.number_input("Quantity", min_value=1, step=1)
    add_btn = st.form_submit_button("Add to Cart")

if add_btn:
    cursor.execute(
        "SELECT name, selling_price, quantity FROM products WHERE product_id=?",
        (product_id,)
    )
    product = cursor.fetchone()

    if product:
        name, price, stock_qty = product

        if qty <= stock_qty:
            st.session_state.cart.append({
                "product_id": product_id,
                "name": name,
                "price": price,
                "qty": qty,
                "total": price * qty
            })
            st.success(f"Added {name} to cart")
        else:
            st.error("Not enough stock")
    else:
        st.error("Invalid Product ID")

# Show cart
st.subheader("🧾 Cart")

if st.session_state.cart:
    grand_total = 0

    for index, item in enumerate(st.session_state.cart):
        col1, col2 = st.columns([4, 1])

        with col1:
            st.write(
                f"{item['name']} | Qty: {item['qty']} | ₹{item['total']}"
            )

        with col2:
            if st.button("❌ Remove", key=f"remove_{index}"):
                st.session_state.cart.pop(index)
                st.rerun()

        grand_total += item["total"]

    st.markdown(f"### 💰 Total: ₹ {grand_total}")

    if st.button("Generate Bill"):
        # Save order
        cursor.execute(
            "INSERT INTO orders (total_amount) VALUES (?)",
            (grand_total,)
        )
        order_id = cursor.lastrowid

        # Update inventory & order items
        for item in st.session_state.cart:
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
            """, (order_id, item["product_id"], item["qty"], item["price"]))

            cursor.execute("""
                UPDATE products
                SET quantity = quantity - ?
                WHERE product_id = ?
            """, (item["qty"], item["product_id"]))

        conn.commit()

        # Generate PDF bill
        os.makedirs("bills", exist_ok=True)
        bill_path = f"bills/bill_{order_id}.pdf"

        pdf = canvas.Canvas(bill_path, pagesize=A4)
        pdf.setFont("Helvetica", 12)

        y = 800
        pdf.drawString(50, y, "INVOICE")
        y -= 30
        pdf.drawString(50, y, f"Order ID: {order_id}")
        y -= 20
        pdf.drawString(50, y, f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M')}")
        y -= 30

        for item in st.session_state.cart:
            pdf.drawString(
                50, y,
                f"{item['name']} | Qty {item['qty']} | ₹ {item['total']}"
            )
            y -= 20

        y -= 20
        pdf.drawString(50, y, f"Total Amount: ₹ {grand_total}")
        pdf.save()

        st.success("Bill Generated Successfully 🎉")

        with open(bill_path, "rb") as f:
            st.download_button(
                "⬇️ Download Bill (PDF)",
                f,
                file_name=f"bill_{order_id}.pdf"
            )

        st.session_state.cart = []
else:
    st.info("Cart is empty")
