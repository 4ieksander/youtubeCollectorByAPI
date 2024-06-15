import sqlite3
db_name = 'API_youtube_app.db'

def initialize_db():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL)''')

    c.execute('''CREATE TABLE IF NOT EXISTS movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    user_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users (id))''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_db()
