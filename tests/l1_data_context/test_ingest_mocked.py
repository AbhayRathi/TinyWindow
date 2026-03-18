"""Tests for ingest adapters using mocked API responses (no real API calls)."""

from unittest.mock import MagicMock, patch
import pandas as pd
import pytest

from data_context.config import AlpacaConfig, BinanceConfig, RedditConfig, TwitterConfig


# ---------- AlpacaSource ----------


class TestAlpacaSource:
    @patch("data_context.ingest.alpaca_source.StockHistoricalDataClient")
    def test_fetch_ohlcv_returns_dataframe(self, mock_client_cls):
        """AlpacaSource.fetch_ohlcv should return a DataFrame with OHLCV columns."""
        from data_context.ingest.alpaca_source import AlpacaSource

        # Build a mock bars response
        dates = pd.date_range("2023-01-01", periods=5, freq="D", tz="UTC")
        mock_df = pd.DataFrame(
            {
                "open": [100, 101, 102, 103, 104],
                "high": [105, 106, 107, 108, 109],
                "low": [95, 96, 97, 98, 99],
                "close": [102, 103, 104, 105, 106],
                "volume": [1000, 1100, 1200, 1300, 1400],
                "extra_col": [0, 0, 0, 0, 0],
            },
            index=dates,
        )
        mock_bars = MagicMock()
        mock_bars.df = mock_df
        mock_client_cls.return_value.get_stock_bars.return_value = mock_bars

        config = AlpacaConfig(api_key="test", api_secret="test")
        source = AlpacaSource(config)
        result = source.fetch_ohlcv("AAPL", "2023-01-01", "2023-01-06")

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["open", "high", "low", "close", "volume"]
        assert len(result) == 5

    @patch("data_context.ingest.alpaca_source.StockHistoricalDataClient")
    def test_fetch_ohlcv_handles_multiindex(self, mock_client_cls):
        """AlpacaSource should handle MultiIndex responses correctly."""
        from data_context.ingest.alpaca_source import AlpacaSource

        dates = pd.date_range("2023-01-01", periods=3, freq="D", tz="UTC")
        arrays = [["AAPL"] * 3, dates]
        index = pd.MultiIndex.from_arrays(arrays, names=["symbol", "timestamp"])
        mock_df = pd.DataFrame(
            {
                "open": [100, 101, 102],
                "high": [105, 106, 107],
                "low": [95, 96, 97],
                "close": [102, 103, 104],
                "volume": [1000, 1100, 1200],
            },
            index=index,
        )
        mock_bars = MagicMock()
        mock_bars.df = mock_df
        mock_client_cls.return_value.get_stock_bars.return_value = mock_bars

        config = AlpacaConfig(api_key="test", api_secret="test")
        source = AlpacaSource(config)
        result = source.fetch_ohlcv("AAPL", "2023-01-01", "2023-01-04")

        assert not isinstance(result.index, pd.MultiIndex)
        assert len(result) == 3

    @patch("data_context.ingest.alpaca_source.StockHistoricalDataClient")
    def test_name(self, mock_client_cls):
        from data_context.ingest.alpaca_source import AlpacaSource

        config = AlpacaConfig(api_key="test", api_secret="test")
        source = AlpacaSource(config)
        assert source.name() == "AlpacaSource"


# ---------- YahooSource ----------


class TestYahooSource:
    @patch("data_context.ingest.yahoo_source.yf")
    def test_fetch_ohlcv_returns_dataframe(self, mock_yf):
        from data_context.ingest.yahoo_source import YahooSource

        dates = pd.date_range("2023-01-01", periods=5, freq="D")
        mock_df = pd.DataFrame(
            {
                "Open": [100, 101, 102, 103, 104],
                "High": [105, 106, 107, 108, 109],
                "Low": [95, 96, 97, 98, 99],
                "Close": [102, 103, 104, 105, 106],
                "Volume": [1000, 1100, 1200, 1300, 1400],
            },
            index=dates,
        )
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = mock_df
        mock_yf.Ticker.return_value = mock_ticker

        source = YahooSource()
        result = source.fetch_ohlcv("AAPL", "2023-01-01", "2023-01-06")

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["open", "high", "low", "close", "volume"]
        assert len(result) == 5
        assert result.index.name == "timestamp"

    @patch("data_context.ingest.yahoo_source.yf")
    def test_name(self, mock_yf):
        from data_context.ingest.yahoo_source import YahooSource

        source = YahooSource()
        assert source.name() == "YahooSource"


# ---------- BinanceSource ----------


class TestBinanceSource:
    @patch("data_context.ingest.binance_source.Client")
    def test_fetch_ohlcv_returns_dataframe(self, mock_client_cls):
        from data_context.ingest.binance_source import BinanceSource

        mock_klines = [
            [
                1672531200000,  # timestamp
                "16500.0",
                "16600.0",
                "16400.0",
                "16550.0",
                "100.0",
                1672617599999,
                "1655000.0",
                500,
                "50.0",
                "825000.0",
                "0",
            ],
            [
                1672617600000,
                "16550.0",
                "16700.0",
                "16500.0",
                "16650.0",
                "150.0",
                1672703999999,
                "2497500.0",
                600,
                "75.0",
                "1248750.0",
                "0",
            ],
        ]
        mock_client_cls.return_value.get_historical_klines.return_value = mock_klines

        config = BinanceConfig(api_key="test", api_secret="test")
        source = BinanceSource(config)
        result = source.fetch_ohlcv("BTCUSDT", "2023-01-01", "2023-01-03")

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["open", "high", "low", "close", "volume"]
        assert len(result) == 2

    @patch("data_context.ingest.binance_source.Client")
    def test_fetch_funding_rates(self, mock_client_cls):
        from data_context.ingest.binance_source import BinanceSource

        mock_rates = [
            {
                "symbol": "BTCUSDT",
                "fundingTime": 1672531200000,
                "fundingRate": "0.0001",
            },
            {
                "symbol": "BTCUSDT",
                "fundingTime": 1672560000000,
                "fundingRate": "-0.0002",
            },
        ]
        mock_client_cls.return_value.futures_funding_rate.return_value = mock_rates

        config = BinanceConfig(api_key="test", api_secret="test")
        source = BinanceSource(config)
        result = source.fetch_funding_rates("BTCUSDT", limit=2)

        assert isinstance(result, pd.DataFrame)
        assert "symbol" in result.columns
        assert "rate" in result.columns
        assert len(result) == 2

    @patch("data_context.ingest.binance_source.Client")
    def test_name(self, mock_client_cls):
        from data_context.ingest.binance_source import BinanceSource

        config = BinanceConfig(api_key="test", api_secret="test")
        source = BinanceSource(config)
        assert source.name() == "BinanceSource"


# ---------- RedditSource ----------


class TestRedditSource:
    @patch("data_context.ingest.reddit_source.praw")
    @patch("data_context.ingest.reddit_source.SentimentIntensityAnalyzer")
    def test_fetch_sentiment_returns_dataframe(self, mock_vader, mock_praw):
        from data_context.ingest.reddit_source import RedditSource

        # Mock VADER
        mock_analyzer = MagicMock()
        mock_analyzer.polarity_scores.return_value = {"compound": 0.5}
        mock_vader.return_value = mock_analyzer

        # Mock Reddit posts
        mock_post = MagicMock()
        mock_post.title = "AAPL is going up"
        mock_post.selftext = "I think Apple will do well"
        mock_post.created_utc = 1700000000.0
        mock_post.permalink = "/r/stocks/comments/123"

        mock_subreddit = MagicMock()
        mock_subreddit.search.return_value = [mock_post]
        mock_praw.Reddit.return_value.subreddit.return_value = mock_subreddit

        config = RedditConfig(
            client_id="test", client_secret="test", user_agent="test"
        )
        source = RedditSource(config)
        result = source.fetch_sentiment("AAPL", subreddits=["stocks"])

        assert isinstance(result, pd.DataFrame)
        assert "sentiment_score" in result.columns
        assert "platform" in result.columns
        assert len(result) == 1
        assert result.iloc[0]["platform"] == "reddit"

    @patch("data_context.ingest.reddit_source.praw")
    @patch("data_context.ingest.reddit_source.SentimentIntensityAnalyzer")
    def test_fetch_sentiment_empty_results(self, mock_vader, mock_praw):
        from data_context.ingest.reddit_source import RedditSource

        mock_vader.return_value = MagicMock()
        mock_subreddit = MagicMock()
        mock_subreddit.search.return_value = []
        mock_praw.Reddit.return_value.subreddit.return_value = mock_subreddit

        config = RedditConfig(
            client_id="test", client_secret="test", user_agent="test"
        )
        source = RedditSource(config)
        result = source.fetch_sentiment("AAPL", subreddits=["stocks"])

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


# ---------- TwitterSource ----------


class TestTwitterSource:
    @patch("data_context.ingest.twitter_source.tweepy")
    @patch("data_context.ingest.twitter_source.SentimentIntensityAnalyzer")
    def test_fetch_sentiment_returns_dataframe(self, mock_vader, mock_tweepy):
        from data_context.ingest.twitter_source import TwitterSource

        mock_analyzer = MagicMock()
        mock_analyzer.polarity_scores.return_value = {"compound": 0.7}
        mock_vader.return_value = mock_analyzer

        mock_tweet = MagicMock()
        mock_tweet.text = "$AAPL is bullish!"
        mock_tweet.created_at = "2023-11-01T12:00:00Z"
        mock_tweet.id = "12345"

        mock_response = MagicMock()
        mock_response.data = [mock_tweet]
        mock_tweepy.Client.return_value.search_recent_tweets.return_value = (
            mock_response
        )

        config = TwitterConfig(bearer_token="test")
        source = TwitterSource(config)
        result = source.fetch_sentiment("AAPL")

        assert isinstance(result, pd.DataFrame)
        assert "sentiment_score" in result.columns
        assert "platform" in result.columns
        assert len(result) == 1
        assert result.iloc[0]["platform"] == "twitter"

    @patch("data_context.ingest.twitter_source.tweepy")
    @patch("data_context.ingest.twitter_source.SentimentIntensityAnalyzer")
    def test_fetch_sentiment_empty_results(self, mock_vader, mock_tweepy):
        from data_context.ingest.twitter_source import TwitterSource

        mock_vader.return_value = MagicMock()
        mock_response = MagicMock()
        mock_response.data = None
        mock_tweepy.Client.return_value.search_recent_tweets.return_value = (
            mock_response
        )

        config = TwitterConfig(bearer_token="test")
        source = TwitterSource(config)
        result = source.fetch_sentiment("AAPL")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
