# init_db.py
import os, sqlite3

DB_PATH = "microevents.db"

SCHEMA = r"""
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_salt TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'admin',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    date TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    price INTEGER NOT NULL CHECK (price >= 0),
    initial_quota INTEGER NOT NULL CHECK (initial_quota >= 0),
    current_quota INTEGER NOT NULL CHECK (current_quota >= 0),
    is_sold_out INTEGER NOT NULL DEFAULT 0,
    created_by INTEGER NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS ticket_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('SALE','REFUND')),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    performed_by INTEGER NOT NULL,
    note TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (performed_by) REFERENCES users(id) ON DELETE RESTRICT
);

INSERT OR IGNORE INTO categories(name) VALUES ('Charla');
INSERT OR IGNORE INTO categories(name) VALUES ('Taller');
INSERT OR IGNORE INTO categories(name) VALUES ('Show');
"""

def main():
    first_time = not os.path.exists(DB_PATH)
    with sqlite3.connect(DB_PATH) as con:
        con.executescript(SCHEMA)
    print(f"Base creada/actualizada en: {DB_PATH}")
    if first_time:
        print("Seed de categorías aplicado. Crea el usuario admin desde tu app o script aparte.")

if __name__ == "__main__":
    main()
