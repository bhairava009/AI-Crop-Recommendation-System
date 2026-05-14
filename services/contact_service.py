import sqlite3
import os
import datetime

DB_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'instance', 'users.db')

def init_contact_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT,
            message TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_message(name, email, subject, message):
    init_contact_db()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (timestamp, name, email, subject, message)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, name, email, subject, message))
    conn.commit()
    conn.close()

def get_all_messages():
    init_contact_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM messages ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
