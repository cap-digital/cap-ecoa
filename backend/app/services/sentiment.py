from textblob import TextBlob
from typing import Tuple


def analyze_sentiment(text: str) -> Tuple[str, float]:
    """
    Analyze sentiment of text using TextBlob.
    Returns tuple of (sentiment_label, sentiment_score)

    Score ranges from -1 (negative) to 1 (positive)
    """
    if not text:
        return "neutral", 0.0

    # TextBlob analysis
    blob = TextBlob(text)
    score = blob.sentiment.polarity

    # Classify sentiment
    if score > 0.1:
        label = "positive"
    elif score < -0.1:
        label = "negative"
    else:
        label = "neutral"

    return label, round(score, 3)


def analyze_news_sentiment(title: str, content: str = None) -> Tuple[str, float]:
    """
    Analyze sentiment of a news article.
    Gives more weight to title but also considers content.
    """
    title_label, title_score = analyze_sentiment(title)

    if content:
        content_label, content_score = analyze_sentiment(content)
        # Weight: 60% title, 40% content
        combined_score = (title_score * 0.6) + (content_score * 0.4)
    else:
        combined_score = title_score

    # Classify combined sentiment
    if combined_score > 0.1:
        label = "positive"
    elif combined_score < -0.1:
        label = "negative"
    else:
        label = "neutral"

    return label, round(combined_score, 3)
