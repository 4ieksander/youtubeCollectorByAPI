import sqlite3
from hashlib import sha256
from datetime import datetime, timedelta
from .db_setup import db_name, initialize_db

def register_user(username, password, role):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    hashed_password = sha256(password.encode()).hexdigest()

    try:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  (username, hashed_password, role))
        conn.commit()
        return True
    except sqlite3.OperationalError:
        initialize_db()
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
          (username, hashed_password, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        conn.close()


def login_user(username, password):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    hashed_password = sha256(password.encode()).hexdigest()
    try:
        c.execute("SELECT * FROM users WHERE username=?", (username,))
    except sqlite3.OperationalError:
        initialize_db()
        c.execute("SELECT * FROM users WHERE username=?", (username,))

    user = c.fetchone()
    try:
        if user and user[4] and datetime.strptime(user[4], "%Y-%m-%d %H:%M:%S") > datetime.now():
            return None  # user is blocked
    except TypeError:
        pass

    if user and user[2] == hashed_password:
        return user
    conn.close()
    return None


def block_user(user_id, duration_minutes):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    blocked_until = datetime.now() + timedelta(minutes=duration_minutes)
    c.execute("UPDATE users SET blocked_until=? WHERE id=?", (blocked_until, user_id))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.close()
    return users