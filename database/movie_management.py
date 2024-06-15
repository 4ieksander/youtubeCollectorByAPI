import sqlite3
from .db_setup import db_name

def add_movie(video_data, user_id):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("INSERT INTO movies (title, published_at, views, likes, user_id) VALUES (?, ?, ?, ?, ?)",
              (video_data["title"], video_data["published_at"], video_data["views"], video_data["likes"], user_id))
    conn.commit()
    conn.close()

def delete_movie(movie_id):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("DELETE FROM movies WHERE id=?", (movie_id,))
    conn.commit()
    conn.close()

def get_user_movies(user_id):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT * FROM movies WHERE user_id=?", (user_id,))
    movies = c.fetchall()
    conn.close()
    return movies

def get_all_movies():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT * FROM movies")
    movies = c.fetchall()
    conn.close()
    return movies

def get_all_users():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.close()
    return users
