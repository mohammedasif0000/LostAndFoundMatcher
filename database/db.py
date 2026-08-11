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

def create_users_table():
    connection = get_db_connection()
    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()

def add_user(username, email, password_hash):
    connection = get_db_connection()
    try:
        connection.execute(
            """
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (username, email, password_hash)
        )
        connection.commit()
    except sqlite3.IntegrityError:
        connection.close()
        return False
    connection.close()
    return True

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

def get_users():
    connection = get_db_connection()
    users = connection.execute("SELECT * FROM Users").fetchall()
    connection.close()
    return users

def get_user_by_username(username):
    connection = get_db_connection()

    user = connection.execute(
        "SELECT * FROM Users WHERE username = ?",
        (username,)
    ).fetchone()

    connection.close()
    return user

if __name__=="__main__":
    create_table()
    create_users_table()
    print("Database ready")