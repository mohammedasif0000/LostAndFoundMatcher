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
            contact TEXT NOT NULL,
            identifying_feature TEXT,
            secret_detail TEXT
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

def add_item(item_type,item_name,category,description,location,date,image,contact,identifying_feature,secret_detail):
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
            contact,
            identifying_feature,
            secret_detail
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        item_type,
        item_name,
        category,
        description,
        location,
        date,
        image,
        contact,
        identifying_feature,
        secret_detail
    ))
    connection.commit()
    item_id = connection.execute("SELECT last_insert_rowid()").fetchone()[0]
    connection.close()
    return item_id

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

def get_user_by_id(user_id):
    connection = get_db_connection()
    user = connection.execute(
        "SELECT * FROM Users WHERE id = ?",
        (user_id,)
    ).fetchone()
    connection.close()
    return user

def get_user_by_email(email):
    connection = get_db_connection()
    user = connection.execute(
        "SELECT * FROM Users WHERE email = ?",
        (email,)
    ).fetchone()
    connection.close()
    return user

def update_password(email, password_hash):
    connection = get_db_connection()
    connection.execute(
        """
        UPDATE Users
        SET password_hash = ?
        WHERE email = ?
        """,
        (password_hash, email)
    )
    connection.commit()
    connection.close()

def update_items_table():
    connection = get_db_connection()
    try:
        connection.execute(
            "ALTER TABLE Items ADD COLUMN identifying_feature TEXT"
        )
        connection.execute(
            "ALTER TABLE Items ADD COLUMN secret_detail TEXT"
        )
        connection.commit()
        print("Items table updated")
    except sqlite3.OperationalError as error:
        print("Update:", error)
    finally:
        connection.close()

def create_verification_table():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS Verification (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            claimant_id INTEGER NOT NULL,
            identifying_feature TEXT,
            secret_detail TEXT,
            location TEXT,
            date TEXT,
            description TEXT,
            score INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()
    print("Verification table ready")

if __name__=="__main__":
    create_table()
    create_users_table()
    update_items_table()
    create_verification_table()
    print("Database ready")