import sqlite3

# Connect to database (it will create the file if not exist)
conn = sqlite3.connect('clients.db')

# Create a cursor to execute SQL commands
cursor = conn.cursor()

# Create a table for clients
cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

# Commit changes and close connection
conn.commit()
conn.close()

print("Database and clients table created successfully!")
