import sqlite3
from config import Config

def check_database():
    conn = sqlite3.connect(Config.DATABASE)
    cursor = conn.cursor()

    # Check Requests Table
    print("\n📌 Requests Table:")
    cursor.execute("SELECT * FROM requests")
    for row in cursor.fetchall():
        print(row)

    # Check Products Table
    print("\n📌 Products Table:")
    cursor.execute("SELECT * FROM products")
    for row in cursor.fetchall():
        print(row)

    conn.close()

check_database()
