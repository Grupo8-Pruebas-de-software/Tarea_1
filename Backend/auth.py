import sqlite3, hashlib, os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "microevents.db")
DB_PATH = os.path.abspath(DB_PATH)

def hash_password(password: str, salt: str = None):
    if not salt:
        salt = os.urandom(16).hex()
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return salt, hashed

def create_user(name: str, email: str, password: str):
    salt, hashed = hash_password(password)
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        try:
            cur.execute(
                "INSERT INTO users (name, email, password_salt, password_hash, role) VALUES (?, ?, ?, ?, ?)",
                (name, email, salt, hashed, "admin"),
            )
            con.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def verify_user(email: str, password: str):
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT id, password_salt, password_hash FROM users WHERE email = ?", (email,))
        row = cur.fetchone()
        if not row:
            return None
        uid, salt, stored_hash = row
        _, hashed = hash_password(password, salt)
        return uid if hashed == stored_hash else None
