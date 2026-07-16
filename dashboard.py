from flask import Blueprint, render_template, session

from auth import login_required
from repositories import ReviewRepository

dashboard_bp = Blueprint("dashboard", __name__)
review_repository = ReviewRepository()


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    summary = review_repository.get_summary_for_user(session["user_id"])
    percentages = {}
    for key in ("positive", "negative", "neutral", "undefined"):
        percentages[key] = round((getattr(summary, key) / summary.total) * 100) if summary.total else 0
    return render_template("dashboard.html", summary=summary, percentages=percentages)
