"""Reddit sentiment data source adapter."""
import pandas as pd
import praw
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from data_context.config import RedditConfig


DEFAULT_SUBREDDITS = ["wallstreetbets", "stocks", "investing", "CryptoCurrency"]


class RedditSource:
    """Fetches posts from financial subreddits and scores sentiment."""

    def __init__(self, config: RedditConfig):
        self._reddit = praw.Reddit(
            client_id=config.client_id,
            client_secret=config.client_secret,
            user_agent=config.user_agent,
        )
        self._analyzer = SentimentIntensityAnalyzer()

    def fetch_sentiment(
        self,
        symbol: str,
        subreddits: list[str] | None = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        """Search subreddits for posts mentioning symbol, score sentiment.

        Returns:
            DataFrame with columns:
                [timestamp, symbol, platform, text, sentiment_score, source_url]
        """
        subreddits = subreddits or DEFAULT_SUBREDDITS
        records = []

        for sub_name in subreddits:
            subreddit = self._reddit.subreddit(sub_name)
            for post in subreddit.search(symbol, limit=limit, sort="new"):
                text = f"{post.title} {post.selftext}".strip()
                score = self._analyzer.polarity_scores(text)["compound"]
                records.append(
                    {
                        "timestamp": int(post.created_utc * 1000),
                        "symbol": symbol,
                        "platform": "reddit",
                        "text": text[:500],  # truncate
                        "sentiment_score": score,
                        "source_url": f"https://reddit.com{post.permalink}",
                    }
                )

        if not records:
            return pd.DataFrame(
                columns=[
                    "timestamp",
                    "symbol",
                    "platform",
                    "text",
                    "sentiment_score",
                    "source_url",
                ]
            )

        df = pd.DataFrame(records)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        return df.sort_values("timestamp").reset_index(drop=True)
