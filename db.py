import sqlite3
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash

DB_PATH = "sentify.db"

DEMO_USERS = [
    ("demo@sentify.com", "demo1234"),
    ("manager@sentify.com", "manager123"),
]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS event_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    existing = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if existing == 0:
        for email, password in DEMO_USERS:
            conn.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (email, generate_password_hash(password)),
            )

    conn.commit()
    conn.close()


def log_event(user_id, event_type):
    conn = get_db()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
    conn.execute("DELETE FROM event_log WHERE created_at < ?", (cutoff,))
    conn.execute(
        "INSERT INTO event_log (user_id, event_type, created_at) VALUES (?, ?, ?)",
        (user_id, event_type, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()
