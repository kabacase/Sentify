import csv
import io

from flask import Blueprint, render_template, request, session

from auth import login_required
from classifier import SentimentClassifier
from models import SentimentSummary
from repositories import ReviewRepository

upload_bp = Blueprint("upload", __name__)
review_repository = ReviewRepository()
classifier = SentimentClassifier()

# columns we'll look for in the uploaded CSV, in order of preference
LIKELY_COLUMN_NAMES = ["review", "review_text", "text", "comment", "feedback"]

# Analyze Sentiment data definition: Review Text, Len = 1000
MAX_REVIEW_LENGTH = 1000


def _find_review_column(fieldnames):
    """Pick whichever column has the review text, falling back to the first column."""
    for name in fieldnames:
        if name.strip().lower() in LIKELY_COLUMN_NAMES:
            return name
    return fieldnames[0]


@upload_bp.route("/upload", methods=["GET", "POST"])
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
                    column = _find_review_column(reader.fieldnames)
                    results = []
                    for row in reader:
                        text = (row.get(column) or "").strip()[:MAX_REVIEW_LENGTH]
                        sentiment = classifier.classify(text)
                        review_repository.create_review(session["user_id"], text, sentiment)
                        results.append({"text": text, "sentiment": sentiment})

                    if not results:
                        error = "No rows found in that file."
                    else:
                        summary = SentimentSummary(
                            total=len(results),
                            positive=sum(1 for r in results if r["sentiment"] == "Positive"),
                            negative=sum(1 for r in results if r["sentiment"] == "Negative"),
                            neutral=sum(1 for r in results if r["sentiment"] == "Neutral"),
                            undefined=sum(1 for r in results if r["sentiment"] == "Undefined"),
                        )
            except Exception:
                error = "Couldn't read that file. Make sure it's a valid CSV."

    return render_template("upload.html", results=results, error=error, summary=summary)
