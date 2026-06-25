import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect("database/company.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS Employee (
    id INTEGER PRIMARY KEY,
    name TEXT,
    salary INTEGER,
    department TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS Students (
    id INTEGER PRIMARY KEY,
    name TEXT,
    cgpa REAL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    email TEXT,
    password_hash TEXT,
    role TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS QueryHistory (
    id INTEGER PRIMARY KEY,
    username TEXT,
    prompt TEXT,
    generated_sql TEXT,
    status TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Insert dummy data
cur.execute("INSERT OR IGNORE INTO Employee (id, name, salary, department) VALUES (1, 'Rahul', 60000, 'IT'), (2, 'Aman', 45000, 'HR'), (3, 'Riya', 80000, 'IT'), (4, 'Neha', 65000, 'Finance')")
cur.execute("INSERT OR IGNORE INTO Students (id, name, cgpa) VALUES (1, 'Ankit', 9.2), (2, 'Priya', 8.9), (3, 'Karan', 9.5)")

# Insert default admin user (password: admin123)
admin_hash = generate_password_hash("admin123")
cur.execute("INSERT OR IGNORE INTO Users (username, email, password_hash, role) VALUES ('admin', 'admin@example.com', ?, 'admin')", (admin_hash,))

conn.commit()
conn.close()
print("Database created and seeded.")