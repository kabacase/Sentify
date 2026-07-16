# Sentify - Review sentiment analyzer

## What this is
A Flask app that classifies customer reviews as Positive, Negative, Neutral, or
Undefined using a free sentiment library (VADER) - no API key needed. Covers the 5
features for this sprint: Authenticate, Upload Reviews, Analyze Sentiment, View
Dashboard, Export Results.

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

## Logging in
There's no self-service signup - log in with one of the seeded demo accounts:

- demo@sentify.com / demo1234
- manager@sentify.com / manager123

## Using it
1. Log in.
2. On the Upload page, upload a CSV of customer reviews (sample_reviews.csv is
   included). Your CSV just needs one column with the review text in it (the app
   looks for a column named "review", "text", "comment", or "feedback" - if it can't
   find one, it uses the first column).
3. Each row gets classified and saved. Rows with no readable text are marked
   Undefined instead of being dropped.
4. Visit the Dashboard to see the aggregate sentiment breakdown for your account.
5. Export your results as CSV or PDF from the Dashboard.

