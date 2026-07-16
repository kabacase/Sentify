from dataclasses import dataclass


@dataclass
class SentimentSummary:
    total: int
    positive: int
    negative: int
    neutral: int
    undefined: int
