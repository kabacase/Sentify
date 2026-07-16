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


def get_user_by_email(email):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return user


def create_review(user_id, text, sentiment):
    conn = get_db()
    conn.execute(
        "INSERT INTO reviews (user_id, text, sentiment, created_at) VALUES (?, ?, ?, ?)",
        (user_id, text, sentiment, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_reviews_for_user(user_id):
    conn = get_db()
    reviews = conn.execute(
        "SELECT * FROM reviews WHERE user_id = ? ORDER BY id DESC", (user_id,)
    ).fetchall()
    conn.close()
    return reviews


def get_summary_for_user(user_id):
    reviews = get_reviews_for_user(user_id)
    summary = {"total": len(reviews), "positive": 0, "negative": 0, "neutral": 0, "undefined": 0}
    for review in reviews:
        key = review["sentiment"].lower()
        if key in summary:
            summary[key] += 1
    return summary


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
