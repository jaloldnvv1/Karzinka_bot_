import sqlite3
from config import DB_NAME, DEFAULT_ADMIN_ID


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        category TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins (
        user_id INTEGER PRIMARY KEY
    )
    ''')

    cursor.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (DEFAULT_ADMIN_ID,))

    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ('Non', 5000, 'Non mahsulotlari'),
            ('Sut', 12000, 'Sut mahsulotlari'),
            ('Guruch', 15000, 'Oziq-ovqat'),
            ('Shakar', 10000, 'Oziq-ovqat'),
            ('Coca-Cola', 13000, 'Ichimliklar'),
            ('Shokolad', 18000, 'Shirinliklar')
        ]
        cursor.executemany("INSERT INTO products (name, price, category) VALUES (?, ?, ?)", sample_products)

    conn.commit()
    conn.close()


def get_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM products")
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categories


def get_products_by_category(category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price FROM products WHERE category = ?", (category,))
    products = cursor.fetchall()
    conn.close()
    return products


def get_product(product_id):
    """Get product by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, category FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product


def add_to_cart(user_id, product_id, quantity=1):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    existing = cursor.fetchone()

    if existing:
        new_quantity = existing[0] + quantity
        cursor.execute("UPDATE cart SET quantity = ? WHERE user_id = ? AND product_id = ?",
                       (new_quantity, user_id, product_id))
    else:
        cursor.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)",
                       (user_id, product_id, quantity))

    conn.commit()
    conn.close()


def remove_from_cart(user_id, cart_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE id = ? AND user_id = ?", (cart_id, user_id))
    conn.commit()
    conn.close()


def get_cart(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT cart.id, products.name, cart.quantity, products.price 
    FROM cart 
    JOIN products ON cart.product_id = products.id 
    WHERE cart.user_id = ?
    """, (user_id,))
    cart_items = cursor.fetchall()
    conn.close()
    return cart_items


def clear_cart(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def is_admin(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM admins WHERE user_id = ?", (user_id,))
    result = cursor.fetchone() is not None
    conn.close()
    return result


def add_product(name, price, category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, price, category) VALUES (?, ?, ?)",
        (name, price, category)
    )
    conn.commit()
    conn.close()


def update_product_name(product_id, new_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET name = ? WHERE id = ?", (new_name, product_id))
    conn.commit()
    conn.close()


def update_product_price(product_id, new_price):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET price = ? WHERE id = ?", (new_price, product_id))
    conn.commit()
    conn.close()


def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    # First remove from all carts
    cursor.execute("DELETE FROM cart WHERE product_id = ?", (product_id,))

    # Then delete the product
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()


def get_all_products():
    """Get all products"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price FROM products")
    products = cursor.fetchall()
    conn.close()
    return products
