import sqlite3, hashlib, os
from logger_config import logger

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
            logger.info(f"Usuario creado: {email}")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Intento de crear usuario con email ya registrado: {email}")
            return False

def verify_user(email: str, password: str):
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT id, password_salt, password_hash FROM users WHERE email = ?", (email,))
        row = cur.fetchone()
        if not row:
            logger.warning(f"Intento de login fallido (usuario no existe): {email}")
            return None
        uid, salt, stored_hash = row
        _, hashed = hash_password(password, salt)
        if hashed == stored_hash:
            logger.info(f"Login exitoso: {email}")
            return uid
        else:
            logger.warning(f"Intento de login fallido (password incorrecta): {email}")
            return None
