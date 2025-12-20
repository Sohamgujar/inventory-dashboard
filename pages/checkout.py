import streamlit as st
import pandas as pd
from db import conn, cursor, reset_transaction

reset_transaction()

st.title("🛒 Checkout & Billing")

# Load products
cursor.execute("""
    SELECT product_id, name, selling_price, quantity
    FROM products
    WHERE quantity > 0
    ORDER BY name
""")
products = cursor.fetchall()

if not products:
    st.warning("No products available.")
    st.stop()

df = pd.DataFrame(
    products,
    columns=["Product ID", "Name", "Price", "Stock"]
)

# Session cart
if "cart" not in st.session_state:
    st.session_state.cart = []

st.subheader("➕ Add Product")

product_name = st.selectbox("Select Product", df["Name"].tolist())
selected = df[df["Name"] == product_name].iloc[0]

qty = st.number_input(
    "Quantity",
    min_value=1,
    max_value=int(selected["Stock"]),
    step=1
)

if st.button("Add to Cart"):
    st.session_state.cart.append({
        "product_id": int(selected["Product ID"]),
        "name": product_name,
        "price": float(selected["Price"]),
        "quantity": qty,
        "total": qty * float(selected["Price"])
    })
    st.success("Added to cart")

# Cart
st.divider()
st.subheader("🧾 Cart")

if not st.session_state.cart:
    st.info("Cart is empty")
else:
    cart_df = pd.DataFrame(st.session_state.cart)
    st.dataframe(cart_df, use_container_width=True)

    total_amount = cart_df["total"].sum()
    st.markdown(f"### 💰 Total: ₹ {total_amount}")

    if st.button("Place Order"):
        reset_transaction()
        cursor.execute(
            'INSERT INTO "public"."orders" (total_amount) VALUES (%s) RETURNING order_id',
            (total_amount,)
        )

        order_id = cursor.fetchone()[0]

        for item in st.session_state.cart:
            cursor.execute("""
                INSERT INTO "public"."order_items" (order_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (
                order_id,
                item["product_id"],
                item["quantity"],
                item["price"]
            ))

            cursor.execute("""
                UPDATE "public"."products"
                SET quantity = quantity - %s
                WHERE product_id = %s

            """, (
                item["quantity"],
                item["product_id"]
            ))

        conn.commit()
        st.session_state.cart = []
        st.success(f"✅ Order #{order_id} placed successfully")
