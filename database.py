import sqlite3
from config import Config

def get_db():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            request_id TEXT PRIMARY KEY,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT,
            serial_number INTEGER,
            product_name TEXT,
            input_image_urls TEXT,
            output_image_urls TEXT,
            FOREIGN KEY (request_id) REFERENCES requests(request_id)
        )
    ''')
    conn.commit()
    conn.close()

def save_request(request_id, csv_data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO requests (request_id) VALUES (?)", (request_id,))
    for row in csv_data:
        cursor.execute('''
            INSERT INTO products (request_id, serial_number, product_name, input_image_urls)
            VALUES (?, ?, ?, ?)
        ''', (request_id, row['Serial Number'], row['Product Name'], row['Input Image Urls']))
    conn.commit()
    conn.close()

def get_request_status(request_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM requests WHERE request_id = ?", (request_id,))
    result = cursor.fetchone()
    conn.close()
    return result['status'] if result else None

def get_products_by_request(request_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE request_id = ?", (request_id,))
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results]

def update_product_output_urls(product_id, output_urls):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET output_image_urls = ? WHERE id = ?", (output_urls, product_id))
    conn.commit()
    conn.close()

def update_request_status(request_id, status):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE requests SET status = ? WHERE request_id = ?", (status, request_id))
    conn.commit()
    conn.close()