import sqlite3

conn = sqlite3.connect("database/data.db")

cursor = conn.cursor()

cursor.execute("SELECT * FROM sales LIMIT 5")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()