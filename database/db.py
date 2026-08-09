import sqlite3

DATABASE = "database/lost_found.db"

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection

def create_table():
    connection = get_db_connection()
    connection.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            item_name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            location TEXT NOT NULL,
            date TEXT NOT NULL,
            image TEXT,
            contact TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()

def add_item(item_type,item_name,category,description,location,date,image,contact):
    connection = get_db_connection()
    connection.execute("""
        INSERT INTO items (
            type,
            item_name,
            category,
            description,
            location,
            date,
            image,
            contact
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        item_type,
        item_name,
        category,
        description,
        location,
        date,
        image,
        contact
    ))
    connection.commit()
    connection.close()

def get_items():
    connection = get_db_connection()
    items = connection.execute(
        "SELECT * FROM items"
    ).fetchall()
    connection.close()

    return items

if __name__=="__main__":
    create_table()

    add_item(
        "lost",
        "Black Wallet",
        "Wallet",
        "Black leather wallet with college ID",
        "College Canteen",
        "2026-08-09",
        "wallet.jpg",
        "9876543210"
    )

    items = get_items()
    for item in items:
        print(dict(item))