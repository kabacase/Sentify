import csv
import io

from flask import Blueprint, Response, session
from fpdf import FPDF
from fpdf.enums import XPos, YPos

import db
from auth import login_required
from repositories import ReviewRepository

export_bp = Blueprint("export", __name__)
review_repository = ReviewRepository()


def escape_formula(value):
    """Prevent spreadsheet apps from treating exported text as a formula."""
    if value and value[0] in ("=", "+", "-", "@"):
        return "'" + value
    return value


def sanitize_for_pdf(text):
    """Replace characters fpdf2's core fonts can't render, collapsing runs into one '?'."""
    result = []
    last_was_replacement = False
    for ch in text:
        try:
            ch.encode("latin-1")
            result.append(ch)
            last_was_replacement = False
        except UnicodeEncodeError:
            if not last_was_replacement:
                result.append("?")
            last_was_replacement = True
    return "".join(result)


@export_bp.route("/export/csv")
@login_required
def export_csv():
    reviews = review_repository.get_reviews_for_user(session["user_id"])
    db.log_event(session["user_id"], "export_csv")
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["review", "sentiment"])
    for review in reviews:
        writer.writerow([escape_formula(review["text"]), review["sentiment"]])

    return Response(
        buffer.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=sentify_results.csv"},
    )


@export_bp.route("/export/pdf")
@login_required
def export_pdf():
    reviews = review_repository.get_reviews_for_user(session["user_id"])
    db.log_event(session["user_id"], "export_pdf")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Sentify Sentiment Results", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 11)
    for review in reviews:
        safe_text = sanitize_for_pdf(review["text"])
        line = f"[{review['sentiment']}] {safe_text}"
        pdf.multi_cell(0, 8, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf_bytes = bytes(pdf.output())
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment; filename=sentify_results.pdf"},
    )
