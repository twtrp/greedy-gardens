import sqlite3

sql_conn = sqlite3.connect('data/records.sqlite')
sql_cursor = sql_conn.cursor()

queries = [
    "SELECT * FROM records ORDER BY score ASC, seed ASC, seed_type ASC;",
    "SELECT * FROM records ORDER BY score DESC, seed ASC, seed_type ASC;",
    "SELECT * FROM records ORDER BY seed ASC, score DESC, seed_type ASC;",
    "SELECT * FROM records ORDER BY seed DESC, score DESC, seed_type ASC;",
    "SELECT * FROM records ORDER BY seed_type ASC, seed ASC, score DESC;",
    "SELECT * FROM records ORDER BY seed_type DESC, seed ASC, score DESC;"
]
sql_cursor.execute(queries[1])

rows = sql_cursor.fetchall()
for row in rows:
    print(row)

sql_conn.close()
