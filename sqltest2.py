import sqlite3

sql_conn = sqlite3.connect('data/records.sqlite')
sql_cursor = sql_conn.cursor()

sql_cursor.execute('''
    INSERT INTO `records` (`score`, `seed`, `seed_type`) VALUES
        (50, 12345678, 'Set Seed'),
        (40, 23456789, 'Random Seed'),
        (30, 34567890, 'Random Seed'),
        (20, 45678901, 'Set Seed'),
        (10, 56789012, 'Random Seed'),
        (50, 23456789, 'Set Seed'),
        (60, 23456789, 'Set Seed') 
''')

sql_conn.commit()
sql_conn.close()