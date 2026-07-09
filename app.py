import csv
import io
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, Response
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from werkzeug.security import check_password_hash
from fpdf import FPDF
from fpdf.enums import XPos, YPos

import db

app = Flask(__name__)
app.secret_key = "sentify-dev-secret"
analyzer = SentimentIntensityAnalyzer()

# columns we'll look for in the uploaded CSV, in order of preference
LIKELY_COLUMN_NAMES = ["review", "review_text", "text", "comment", "feedback"]


def find_review_column(fieldnames):
    """Pick whichever column has the review text, falling back to the first column."""
    for name in fieldnames:
        if name.strip().lower() in LIKELY_COLUMN_NAMES:
            return name
    return fieldnames[0]


def classify(text):
    """Returns 'Positive', 'Negative', 'Neutral', or 'Undefined' for a piece of text."""
    if not text or not text.strip():
        return "Undefined"
    score = analyzer.polarity_scores(text)["compound"]
    if score >= 0.05:
        return "Positive"
    elif score <= -0.05:
        return "Negative"
    else:
        return "Neutral"


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("upload"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        user = db.get_user_by_email(email)
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["email"] = user["email"]
            return redirect(url_for("upload"))
        error = "Invalid email or password."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    results = None
    error = None
    summary = None

    if request.method == "POST":
        uploaded_file = request.files.get("review_file")

        if not uploaded_file or uploaded_file.filename == "":
            error = "Please choose a CSV file first."
        elif not uploaded_file.filename.lower().endswith(".csv"):
            error = "That doesn't look like a CSV file. Please upload a .csv file."
        else:
            try:
                raw_text = uploaded_file.stream.read().decode("utf-8")
                reader = csv.DictReader(io.StringIO(raw_text))

                if not reader.fieldnames:
                    error = "That CSV looks empty."
                else:
                    column = find_review_column(reader.fieldnames)
                    results = []
                    for row in reader:
                        text = (row.get(column) or "").strip()
                        sentiment = classify(text)
                        db.create_review(session["user_id"], text, sentiment)
                        results.append({"text": text, "sentiment": sentiment})

                    if not results:
                        error = "No rows found in that file."
                    else:
                        summary = {
                            "total": len(results),
                            "positive": sum(1 for r in results if r["sentiment"] == "Positive"),
                            "negative": sum(1 for r in results if r["sentiment"] == "Negative"),
                            "neutral": sum(1 for r in results if r["sentiment"] == "Neutral"),
                            "undefined": sum(1 for r in results if r["sentiment"] == "Undefined"),
                        }
            except Exception:
                error = "Couldn't read that file. Make sure it's a valid CSV."

    return render_template("upload.html", results=results, error=error, summary=summary)


@app.route("/dashboard")
@login_required
def dashboard():
    summary = db.get_summary_for_user(session["user_id"])
    percentages = {}
    for key in ("positive", "negative", "neutral", "undefined"):
        percentages[key] = round((summary[key] / summary["total"]) * 100) if summary["total"] else 0
    return render_template("dashboard.html", summary=summary, percentages=percentages)


@app.route("/export/csv")
@login_required
def export_csv():
    reviews = db.get_reviews_for_user(session["user_id"])
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["review", "sentiment"])
    for review in reviews:
        writer.writerow([review["text"], review["sentiment"]])

    return Response(
        buffer.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=sentify_results.csv"},
    )


@app.route("/export/pdf")
@login_required
def export_pdf():
    reviews = db.get_reviews_for_user(session["user_id"])

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Sentify Sentiment Results", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 11)
    for review in reviews:
        line = f"[{review['sentiment']}] {review['text']}"
        pdf.multi_cell(0, 8, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf_bytes = bytes(pdf.output())
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment; filename=sentify_results.pdf"},
    )


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True)
