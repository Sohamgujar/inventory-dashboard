from db import conn, cursor

cursor = conn.cursor()

# Products table
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    cost_price REAL NOT NULL,
    selling_price REAL NOT NULL,
    quantity INTEGER NOT NULL
)
""")

# Orders table
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount REAL
)
""")

# Order items table
cursor.execute("""
CREATE TABLE IF NOT EXISTS order_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    price REAL
)
""")

# Home delivery orders table
cursor.execute("""
CREATE TABLE IF NOT EXISTS home_delivery_orders (
    delivery_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    mobile_number TEXT,
    address TEXT,
    product_id INTEGER,
    product_name TEXT,
    quantity INTEGER,
    price REAL,
    total_amount REAL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
# Add delivery status column safely
try:
    cursor.execute("ALTER TABLE home_delivery_orders ADD COLUMN status TEXT DEFAULT 'Pending'")
except:
    pass

# Ensure delivery status column exists (cloud-safe)
try:
    cursor.execute("ALTER TABLE home_delivery_orders ADD COLUMN status TEXT DEFAULT 'Pending'")
    conn.commit()
except:
    pass


conn.commit()
