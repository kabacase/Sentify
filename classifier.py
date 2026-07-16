from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class SentimentClassifier:
    def __init__(self):
        self._analyzer = SentimentIntensityAnalyzer()

    def classify(self, text):
        """Returns 'Positive', 'Negative', 'Neutral', or 'Undefined' for a piece of text."""
        if not text or not text.strip():
            return "Undefined"
        score = self._analyzer.polarity_scores(text)["compound"]
        if score >= 0.05:
            return "Positive"
        elif score <= -0.05:
            return "Negative"
        else:
            return "Neutral"
