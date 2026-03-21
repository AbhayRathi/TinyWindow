"""Twitter/X sentiment data source adapter (Tweepy v4, API v2)."""

import pandas as pd
import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from data_context.config import TwitterConfig


class TwitterSource:
    """Fetches recent tweets mentioning a symbol and scores sentiment."""

    def __init__(self, config: TwitterConfig):
        self._client = tweepy.Client(bearer_token=config.bearer_token)
        self._analyzer = SentimentIntensityAnalyzer()

    def fetch_sentiment(
        self,
        symbol: str,
        max_results: int = 100,
    ) -> pd.DataFrame:
        """Search recent tweets for cashtag $SYMBOL, score sentiment.

        Returns:
            DataFrame with columns:
                [timestamp, symbol, platform, text, sentiment_score, source_url]
        """
        query = f"${symbol} lang:en -is:retweet"
        response = self._client.search_recent_tweets(
            query=query,
            max_results=min(max_results, 100),
            tweet_fields=["created_at", "text"],
        )

        if not response.data:
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

        records = []
        for tweet in response.data:
            score = self._analyzer.polarity_scores(tweet.text)["compound"]
            records.append(
                {
                    "timestamp": tweet.created_at,
                    "symbol": symbol,
                    "platform": "twitter",
                    "text": tweet.text,
                    "sentiment_score": score,
                    "source_url": f"https://twitter.com/i/web/status/{tweet.id}",
                }
            )

        df = pd.DataFrame(records)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        return df.sort_values("timestamp").reset_index(drop=True)
