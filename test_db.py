import sqlite3

conn = sqlite3.connect('app.db')
c = conn.cursor()
c.execute("SELECT * FROM users")
users = c.fetchall()
print(users)
conn.close()
