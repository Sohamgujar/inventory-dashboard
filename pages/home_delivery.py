import streamlit as st
import sqlite3
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import os

conn = sqlite3.connect("inventory.db", check_same_thread=False)
cursor = conn.cursor()

st.title("🚚 Home Delivery")

# Session cart
if "delivery_cart" not in st.session_state:
    st.session_state.delivery_cart = []

# ---------------- CUSTOMER DETAILS ----------------
st.subheader("👤 Customer Details")
customer_name = st.text_input("Customer Name")
mobile = st.text_input("Mobile Number")
address = st.text_area("Delivery Address")

st.divider()

# ---------------- ADD PRODUCT ----------------
st.subheader("📦 Add Product to Delivery")

with st.form("add_delivery_product"):
    product_id = st.number_input("Product ID", min_value=1, step=1)
    quantity = st.number_input("Quantity", min_value=1, step=1)
    add_btn = st.form_submit_button("Add to Delivery Cart")

if add_btn:
    cursor.execute("""
        SELECT name, selling_price, quantity
        FROM products
        WHERE product_id = ?
    """, (product_id,))
    product = cursor.fetchone()

    if not product:
        st.error("Invalid Product ID")
    else:
        name, price, stock_qty = product

        if quantity > stock_qty:
            st.error("Not enough stock")
        else:
            st.session_state.delivery_cart.append({
                "product_id": product_id,
                "name": name,
                "price": price,
                "qty": quantity,
                "total": price * quantity
            })
            st.success(f"{name} added to delivery cart")

# ---------------- DELIVERY CART ----------------
st.divider()
st.subheader("🧾 Delivery Cart")

if st.session_state.delivery_cart:
    grand_total = 0

    for index, item in enumerate(st.session_state.delivery_cart):
        col1, col2 = st.columns([4, 1])

        with col1:
            st.write(
                f"{item['name']} | Qty: {item['qty']} | ₹ {item['total']}"
            )

        with col2:
            if st.button("❌ Remove", key=f"remove_delivery_{index}"):
                st.session_state.delivery_cart.pop(index)
                st.rerun()

        grand_total += item["total"]

    st.markdown(f"### 💰 Total Amount: ₹ {grand_total}")

    delivery_status = st.selectbox("Delivery Status", ["Pending", "Delivered"])

    if st.button("📄 Generate Delivery Invoice"):
        if not customer_name or not mobile or not address:
            st.error("Please fill customer details")
        else:
            # Save delivery order
            for item in st.session_state.delivery_cart:
                cursor.execute("""
                    INSERT INTO home_delivery_orders
                    (customer_name, mobile_number, address,
                     product_id, product_name, quantity,
                     price, total_amount, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    customer_name, mobile, address,
                    item["product_id"], item["name"],
                    item["qty"], item["price"],
                    item["total"], delivery_status
                ))

                # Reduce inventory
                cursor.execute("""
                    UPDATE products
                    SET quantity = quantity - ?
                    WHERE product_id = ?
                """, (item["qty"], item["product_id"]))

            conn.commit()

            # Generate PDF invoice
            os.makedirs("delivery_bills", exist_ok=True)
            file_name = f"delivery_bills/delivery_{datetime.now().timestamp()}.pdf"

            pdf = canvas.Canvas(file_name, pagesize=A4)
            pdf.setFont("Helvetica", 12)

            y = 800
            pdf.drawString(50, y, "HOME DELIVERY INVOICE")
            y -= 30
            pdf.drawString(50, y, f"Customer: {customer_name}")
            y -= 20
            pdf.drawString(50, y, f"Mobile: {mobile}")
            y -= 20
            pdf.drawString(50, y, f"Address: {address}")
            y -= 20
            pdf.drawString(50, y, f"Status: {delivery_status}")
            y -= 30

            for item in st.session_state.delivery_cart:
                pdf.drawString(
                    50, y,
                    f"{item['name']} | Qty {item['qty']} | ₹ {item['total']}"
                )
                y -= 20

            y -= 20
            pdf.drawString(50, y, f"Total Amount: ₹ {grand_total}")
            pdf.save()

            st.success("Home delivery order placed successfully 🚚")

            with open(file_name, "rb") as f:
                st.download_button(
                    "⬇️ Download Delivery Invoice (PDF)",
                    f,
                    file_name="home_delivery_invoice.pdf"
                )

            st.session_state.delivery_cart = []
else:
    st.info("Delivery cart is empty")
