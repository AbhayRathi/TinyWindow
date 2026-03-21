"""Tests for DataAPI using a mocked MongoDBStore."""

from datetime import datetime, timezone
from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest

from data_context.query.data_api import DataAPI


@pytest.fixture
def mock_store():
    return MagicMock()


@pytest.fixture
def api(mock_store):
    return DataAPI(store=mock_store)


def _make_ohlcv_df(n: int = 100) -> pd.DataFrame:
    """Return a synthetic OHLCV DataFrame large enough for all indicators."""
    np.random.seed(0)
    dates = pd.date_range("2023-01-01", periods=n, freq="D", tz="UTC")
    close = 100 + np.cumsum(np.random.randn(n) * 0.5)
    high = close + np.abs(np.random.randn(n))
    low = close - np.abs(np.random.randn(n))
    open_ = low + (high - low) * np.random.rand(n)
    volume = np.random.randint(1000, 100000, size=n).astype(float)
    return pd.DataFrame(
        {
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        },
        index=dates,
    )


class TestGetOHLCV:
    def test_with_indicators_returns_rsi_column(self, api, mock_store):
        df = _make_ohlcv_df(100)
        mock_store.query_ohlcv.return_value = df

        result = api.get_ohlcv(
            "AAPL", "2023-01-01", "2023-04-10", with_indicators=True, clean=False
        )

        assert "rsi" in result.columns

    def test_with_indicators_returns_all_indicator_columns(self, api, mock_store):
        df = _make_ohlcv_df(100)
        mock_store.query_ohlcv.return_value = df

        result = api.get_ohlcv(
            "AAPL", "2023-01-01", "2023-04-10", with_indicators=True, clean=False
        )

        for col in (
            "rsi",
            "macd",
            "macd_signal",
            "bb_upper",
            "bb_lower",
            "atr",
            "vwap",
            "obv",
        ):
            assert col in result.columns, f"Missing column: {col}"

    def test_empty_store_returns_empty_dataframe(self, api, mock_store):
        mock_store.query_ohlcv.return_value = pd.DataFrame(
            columns=["open", "high", "low", "close", "volume"]
        )

        result = api.get_ohlcv("AAPL", "2023-01-01", "2023-12-31")

        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_without_indicators_no_rsi_column(self, api, mock_store):
        df = _make_ohlcv_df(50)
        mock_store.query_ohlcv.return_value = df

        result = api.get_ohlcv(
            "AAPL", "2023-01-01", "2023-02-19", with_indicators=False, clean=False
        )

        assert "rsi" not in result.columns

    def test_returns_dataframe(self, api, mock_store):
        df = _make_ohlcv_df(30)
        mock_store.query_ohlcv.return_value = df

        result = api.get_ohlcv("AAPL", "2023-01-01", "2023-01-30", clean=False)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 30

    def test_clean_removes_invalid_rows(self, api, mock_store):
        dates = pd.date_range("2023-01-01", periods=3, freq="D", tz="UTC")
        df = pd.DataFrame(
            {
                "open": [100.0, 110.0, 100.0],
                "high": [105.0, 95.0, 105.0],  # row 1: high < low
                "low": [95.0, 100.0, 95.0],
                "close": [102.0, 92.0, 102.0],
                "volume": [1000.0, 1000.0, 1000.0],
            },
            index=dates,
        )
        mock_store.query_ohlcv.return_value = df

        result = api.get_ohlcv("AAPL", "2023-01-01", "2023-01-03", clean=True)

        assert len(result) == 2


class TestGetSentiment:
    def test_returns_dataframe_with_records(self, api, mock_store):
        ts = datetime(2023, 1, 1, tzinfo=timezone.utc)
        docs = [
            {
                "symbol": "AAPL",
                "timestamp": ts,
                "platform": "reddit",
                "text": "AAPL up",
                "sentiment_score": 0.7,
                "source_url": "https://reddit.com/1",
            }
        ]
        mock_store.get_collection.return_value.find.return_value.sort.return_value = (
            docs
        )

        result = api.get_sentiment("AAPL", "2023-01-01", "2023-01-31")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert "platform" in result.columns

    def test_filters_by_platform(self, api, mock_store):
        ts = datetime(2023, 1, 1, tzinfo=timezone.utc)
        docs = [
            {
                "symbol": "AAPL",
                "timestamp": ts,
                "platform": "reddit",
                "text": "AAPL",
                "sentiment_score": 0.5,
                "source_url": "https://reddit.com/1",
            }
        ]
        mock_store.get_collection.return_value.find.return_value.sort.return_value = (
            docs
        )

        result = api.get_sentiment(
            "AAPL", "2023-01-01", "2023-01-31", platform="reddit"
        )

        mock_store.get_collection.assert_called_with("sentiment_data")
        call_args = mock_store.get_collection.return_value.find.call_args
        query = call_args[0][0]
        assert query.get("platform") == "reddit"

    def test_empty_result_returns_empty_dataframe(self, api, mock_store):
        mock_store.get_collection.return_value.find.return_value.sort.return_value = []

        result = api.get_sentiment("AAPL", "2023-01-01", "2023-01-31")

        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_no_platform_filter_omits_platform_key(self, api, mock_store):
        mock_store.get_collection.return_value.find.return_value.sort.return_value = []

        api.get_sentiment("AAPL", "2023-01-01", "2023-01-31", platform=None)

        call_args = mock_store.get_collection.return_value.find.call_args
        query = call_args[0][0]
        assert "platform" not in query


class TestGetFundingRates:
    def test_returns_correct_shape(self, api, mock_store):
        ts1 = datetime(2023, 1, 1, tzinfo=timezone.utc)
        ts2 = datetime(2023, 1, 2, tzinfo=timezone.utc)
        docs = [
            {"symbol": "BTCUSDT", "timestamp": ts1, "rate": 0.0001},
            {"symbol": "BTCUSDT", "timestamp": ts2, "rate": -0.0002},
        ]
        mock_store.get_collection.return_value.find.return_value.sort.return_value = (
            docs
        )

        result = api.get_funding_rates("BTCUSDT", "2023-01-01", "2023-01-31")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "symbol" in result.columns
        assert "rate" in result.columns

    def test_empty_result_returns_empty_dataframe(self, api, mock_store):
        mock_store.get_collection.return_value.find.return_value.sort.return_value = []

        result = api.get_funding_rates("BTCUSDT", "2023-01-01", "2023-01-31")

        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_queries_correct_collection(self, api, mock_store):
        mock_store.get_collection.return_value.find.return_value.sort.return_value = []

        api.get_funding_rates("BTCUSDT", "2023-01-01", "2023-01-31")

        mock_store.get_collection.assert_called_with("funding_rates")
