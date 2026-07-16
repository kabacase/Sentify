from datetime import datetime

from db import get_db
from models import SentimentSummary


class UserRepository:
    def get_user_by_email(self, email):
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        return user


class ReviewRepository:
    def create_review(self, user_id, text, sentiment):
        conn = get_db()
        conn.execute(
            "INSERT INTO reviews (user_id, text, sentiment, created_at) VALUES (?, ?, ?, ?)",
            (user_id, text, sentiment, datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()

    def get_reviews_for_user(self, user_id):
        conn = get_db()
        reviews = conn.execute(
            "SELECT * FROM reviews WHERE user_id = ? ORDER BY id DESC", (user_id,)
        ).fetchall()
        conn.close()
        return reviews

    def get_summary_for_user(self, user_id):
        reviews = self.get_reviews_for_user(user_id)
        summary = SentimentSummary(total=len(reviews), positive=0, negative=0, neutral=0, undefined=0)
        for review in reviews:
            key = review["sentiment"].lower()
            if hasattr(summary, key):
                setattr(summary, key, getattr(summary, key) + 1)
        return summary
