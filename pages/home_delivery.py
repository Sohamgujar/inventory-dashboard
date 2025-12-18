import streamlit as st
import sqlite3

conn = sqlite3.connect("inventory.db", check_same_thread=False)
cursor = conn.cursor()

st.title("🚚 Home Delivery Order")

with st.form("home_delivery_form"):
    customer_name = st.text_input("Customer Name")
    mobile = st.text_input("Mobile Number")
    address = st.text_area("Delivery Address")

    product_id = st.number_input("Product ID", min_value=1, step=1)
    quantity = st.number_input("Quantity", min_value=1, step=1)

    submit = st.form_submit_button("Place Home Delivery Order")

if submit:
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
            st.error("Not enough stock available")
        else:
            total = price * quantity

            # Save delivery order
            cursor.execute("""
                INSERT INTO home_delivery_orders
                (customer_name, mobile_number, address,
                 product_id, product_name, quantity, price, total_amount)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                customer_name, mobile, address,
                product_id, name, quantity, price, total
            ))

            # Reduce inventory
            cursor.execute("""
                UPDATE products
                SET quantity = quantity - ?
                WHERE product_id = ?
            """, (quantity, product_id))

            conn.commit()

            st.success("Home delivery order placed successfully 🚚")
            st.markdown(f"### 💰 Total Amount: ₹ {total}")
