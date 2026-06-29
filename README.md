# Review sentiment analyzer - Sprint 1 demo

## What this is
A small Flask app. You upload a CSV of customer reviews, and it tags each one
as Positive, Negative, or Neutral using a free sentiment library (VADER) -
no API key needed.

## How to run it
1. Open a terminal in this folder.
2. (Optional but recommended) make a virtual environment:
   python -m venv venv
   source venv/bin/activate      (on Windows: venv\Scripts\activate)
3. Install dependencies:
   pip install -r requirements.txt
4. Run the app:
   python app.py
5. Open your browser to http://127.0.0.1:5000
6. Upload sample_reviews.csv (included) to see it work, or use your own CSV.
   Your CSV just needs one column with the review text in it
   (the app looks for a column named "review", "text", "comment", or
   "feedback" - if it can't find one, it just uses the first column).

## What's intentionally not built yet
This only covers the riskiest slice for Sprint 1: upload -> classify -> show
results. Search/filter, export, the full dashboard, and real-time single-review
input are planned for later sprints (or shown as low-fi screens for now).

## Known limitation worth mentioning in the presentation
VADER is a free, lexicon-based tool (not a trained AI model), so it sometimes
misses things like sarcasm or domain-specific negativity (e.g. "overpriced"
without obviously negative words). That's a real, honest limitation to bring up
under "challenges" - it's also the reason a heavier model (like an OpenAI API
call) is on the roadmap for a later sprint.
