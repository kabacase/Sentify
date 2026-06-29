from flask import Flask, render_template, request
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import csv
import io

app = Flask(__name__)
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
    """Returns 'Positive', 'Negative', or 'Neutral' for a piece of text."""
    score = analyzer.polarity_scores(text)["compound"]
    if score >= 0.05:
        return "Positive"
    elif score <= -0.05:
        return "Negative"
    else:
        return "Neutral"


@app.route("/", methods=["GET", "POST"])
def index():
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
                        if text:
                            results.append({
                                "text": text,
                                "sentiment": classify(text),
                            })

                    if not results:
                        error = "No review text found in that file."
                    else:
                        summary = {
                            "total": len(results),
                            "positive": sum(1 for r in results if r["sentiment"] == "Positive"),
                            "negative": sum(1 for r in results if r["sentiment"] == "Negative"),
                            "neutral": sum(1 for r in results if r["sentiment"] == "Neutral"),
                        }
            except Exception:
                error = "Couldn't read that file. Make sure it's a valid CSV."

    return render_template("index.html", results=results, error=error, summary=summary)


if __name__ == "__main__":
    app.run(debug=True)
