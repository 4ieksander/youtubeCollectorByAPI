import sqlite3
from hashlib import sha256
from .db_setup import db_name

def register_user(username, password, role):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    hashed_password = sha256(password.encode()).hexdigest()

    try:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  (username, hashed_password, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    hashed_password = sha256(password.encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_password))

    user = c.fetchone()
    conn.close()
    return user
