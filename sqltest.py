import sqlite3

# Connect to the database (or create it if it doesn't exist)
sql_conn = sqlite3.connect('data/records.sqlite')
sql_cursor = sql_conn.cursor()

# Create a table for high scores
sql_cursor.execute('''
    CREATE TABLE IF NOT EXISTS `records` (
        `score` INTEGER,
        `seed` INTEGER,
        `seed_type` TEXT
    )
''')

# Save the changes and close the connection
sql_conn.commit()
sql_conn.close()
