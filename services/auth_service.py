import sqlite3
import os

DB_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'instance', 'users.db')

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')
    
    # Check if role column exists (for backward compatibility with old DBs)
    cursor.execute("PRAGMA table_info(user)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'role' not in columns:
        cursor.execute("ALTER TABLE user ADD COLUMN role TEXT DEFAULT 'user'")
        
    conn.commit()
    conn.close()

def create_admin_if_not_exists(username="admin", password="adminpassword"):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE username = ?", (username,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO user (username, password, role) VALUES (?, ?, ?)", (username, password, 'admin'))
        conn.commit()
    conn.close()

def signup_user(username, password, role='user'):
    init_db()
    if not username or not password:
        return False, "Username and password cannot be empty"
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
        return True, "Signup successful"
    except sqlite3.IntegrityError:
        return False, "Username already exists"
    finally:
        conn.close()

def login_user(username, password):
    init_db()
    if not username or not password:
        return False, "Username and password cannot be empty", None

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password, role FROM user WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return True, "Login successful", user[3]
    return False, "Invalid credentials", None

def get_all_users():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM user ORDER BY id DESC")
    users = cursor.fetchall()
    conn.close()
    return [{"id": u[0], "username": u[1], "role": u[2]} for u in users]
