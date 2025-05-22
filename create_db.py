import sqlite3

conn = sqlite3.connect('erp.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT NOT NULL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item TEXT NOT NULL,
    amount INTEGER NOT NULL
)
''')

# Seed some data
c.execute("INSERT INTO inventory (name, quantity) VALUES ('Laptop', 10), ('Mouse', 25)")
c.execute("INSERT INTO employees (name, role) VALUES ('John Doe', 'Manager'), ('Jane Smith', 'Developer')")
c.execute("INSERT INTO sales (item, amount) VALUES ('Laptop', 5), ('Mouse', 10)")

conn.commit()
conn.close()

print("Database created and seeded!")

