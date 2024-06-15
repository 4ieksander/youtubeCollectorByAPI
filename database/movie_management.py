import sqlite3

def add_movie(title, description, user_id):
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    c.execute("INSERT INTO movies (title, description, user_id) VALUES (?, ?, ?)",
              (title, description, user_id))
    conn.commit()
    conn.close()

def delete_movie(movie_id):
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    c.execute("DELETE FROM movies WHERE id=?", (movie_id,))
    conn.commit()
    conn.close()

def get_user_movies(user_id):
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM movies WHERE user_id=?", (user_id,))
    movies = c.fetchall()
    conn.close()
    return movies

def get_all_movies():
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM movies")
    movies = c.fetchall()
    conn.close()
    return movies
