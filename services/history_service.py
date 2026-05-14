import sqlite3
import os
import datetime

DB_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'instance', 'users.db')

def init_history_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            soil_type TEXT,
            n REAL,
            p REAL,
            k REAL,
            temperature REAL,
            humidity REAL,
            rainfall REAL,
            top_crop TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_prediction(username, soil_type, n, p, k, temperature, humidity, rainfall, top_crop):
    init_history_db()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO history (username, timestamp, soil_type, n, p, k, temperature, humidity, rainfall, top_crop)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (username, timestamp, soil_type, n, p, k, temperature, humidity, rainfall, top_crop))
    conn.commit()
    conn.close()

def get_user_history(username):
    init_history_db()
    conn = sqlite3.connect(DB_PATH)
    # Using row_factory to get dict-like objects
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp, soil_type, n, p, k, temperature, humidity, rainfall, top_crop
        FROM history 
        WHERE username = ?
        ORDER BY timestamp DESC
    ''', (username,))
    rows = cursor.fetchall()
    conn.close()
    
    # Convert sqlite3.Row objects to dictionaries for easy access in templates/pandas
    return [dict(row) for row in rows]

def clear_user_history(username):
    init_history_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM history
        WHERE username = ?
    ''', (username,))
    conn.commit()
    conn.close()
