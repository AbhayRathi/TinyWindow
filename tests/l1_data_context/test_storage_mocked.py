"""Tests for MongoDBStore using mongomock (no real MongoDB connection)."""

from datetime import datetime, timezone
from unittest.mock import patch

import mongomock
import pandas as pd
import pytest

from data_context.config import MongoConfig


@pytest.fixture
def store():
    """Return a MongoDBStore backed by an in-memory mongomock client."""
    from data_context.storage.mongodb_store import MongoDBStore

    with patch(
        "data_context.storage.mongodb_store.MongoClient",
        mongomock.MongoClient,
    ):
        config = MongoConfig(uri="mongodb://localhost:27017", db_name="test_db")
        yield MongoDBStore(config)


@pytest.fixture
def ohlcv_df():
    dates = pd.date_range("2023-01-01", periods=5, freq="D", tz="UTC")
    return pd.DataFrame(
        {
            "open": [100.0, 101.0, 102.0, 103.0, 104.0],
            "high": [105.0, 106.0, 107.0, 108.0, 109.0],
            "low": [95.0, 96.0, 97.0, 98.0, 99.0],
            "close": [102.0, 103.0, 104.0, 105.0, 106.0],
            "volume": [1000.0, 1100.0, 1200.0, 1300.0, 1400.0],
        },
        index=dates,
    )


@pytest.fixture
def sentiment_df():
    dates = pd.date_range("2023-01-01", periods=3, freq="D", tz="UTC")
    return pd.DataFrame(
        {
            "timestamp": dates,
            "symbol": ["AAPL", "AAPL", "AAPL"],
            "platform": ["reddit", "reddit", "twitter"],
            "text": ["post a", "post b", "tweet c"],
            "sentiment_score": [0.5, -0.3, 0.8],
            "source_url": ["https://reddit.com/1", "https://reddit.com/2", "https://t.co/3"],
        }
    )


@pytest.fixture
def funding_df():
    dates = pd.date_range("2023-01-01", periods=3, freq="8h", tz="UTC")
    df = pd.DataFrame(
        {
            "symbol": ["BTCUSDT", "BTCUSDT", "BTCUSDT"],
            "rate": [0.0001, -0.0002, 0.00015],
        },
        index=dates,
    )
    df.index.name = "timestamp"
    return df


class TestUpsertAndQueryOHLCV:
    def test_upsert_then_query_returns_identical_data(self, store, ohlcv_df):
        store.upsert_ohlcv(ohlcv_df, symbol="AAPL", source="yahoo")
        result = store.query_ohlcv("AAPL", "2023-01-01", "2023-01-05")

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["open", "high", "low", "close", "volume"]
        assert len(result) == 5
        assert isinstance(result.index, pd.DatetimeIndex)

        for col in ["open", "high", "low", "close", "volume"]:
            pd.testing.assert_series_equal(
                result[col].reset_index(drop=True),
                ohlcv_df[col].reset_index(drop=True),
                check_names=False,
            )

    def test_upsert_is_idempotent(self, store, ohlcv_df):
        store.upsert_ohlcv(ohlcv_df, symbol="AAPL", source="yahoo")
        store.upsert_ohlcv(ohlcv_df, symbol="AAPL", source="yahoo")
        result = store.query_ohlcv("AAPL", "2023-01-01", "2023-01-05")
        assert len(result) == 5

    def test_query_empty_result_returns_empty_dataframe(self, store):
        result = store.query_ohlcv("MISSING", "2023-01-01", "2023-01-05")
        assert isinstance(result, pd.DataFrame)
        assert result.empty
        assert list(result.columns) == ["open", "high", "low", "close", "volume"]

    def test_query_respects_date_range(self, store, ohlcv_df):
        store.upsert_ohlcv(ohlcv_df, symbol="AAPL", source="yahoo")
        result = store.query_ohlcv("AAPL", "2023-01-02", "2023-01-03")
        assert len(result) == 2

    def test_result_index_is_sorted(self, store, ohlcv_df):
        store.upsert_ohlcv(ohlcv_df, symbol="AAPL", source="yahoo")
        result = store.query_ohlcv("AAPL", "2023-01-01", "2023-01-05")
        assert result.index.is_monotonic_increasing


class TestUpsertSentiment:
    def test_upsert_sentiment_stores_records(self, store, sentiment_df):
        store.upsert_sentiment(sentiment_df)
        col = store.get_collection("sentiment_data")
        count = col.count_documents({"symbol": "AAPL"})
        assert count == 3

    def test_upsert_sentiment_idempotent(self, store, sentiment_df):
        store.upsert_sentiment(sentiment_df)
        store.upsert_sentiment(sentiment_df)
        col = store.get_collection("sentiment_data")
        count = col.count_documents({"symbol": "AAPL"})
        assert count == 3

    def test_upsert_sentiment_correct_fields(self, store, sentiment_df):
        store.upsert_sentiment(sentiment_df)
        col = store.get_collection("sentiment_data")
        doc = col.find_one({"source_url": "https://reddit.com/1"})
        assert doc is not None
        assert doc["symbol"] == "AAPL"
        assert doc["platform"] == "reddit"
        assert doc["sentiment_score"] == pytest.approx(0.5)


class TestUpsertFundingRates:
    def test_upsert_funding_rates_stores_records(self, store, funding_df):
        store.upsert_funding_rates(funding_df)
        col = store.get_collection("funding_rates")
        count = col.count_documents({"symbol": "BTCUSDT"})
        assert count == 3

    def test_upsert_funding_rates_idempotent(self, store, funding_df):
        store.upsert_funding_rates(funding_df)
        store.upsert_funding_rates(funding_df)
        col = store.get_collection("funding_rates")
        count = col.count_documents({"symbol": "BTCUSDT"})
        assert count == 3

    def test_upsert_funding_rates_correct_values(self, store, funding_df):
        store.upsert_funding_rates(funding_df)
        col = store.get_collection("funding_rates")
        docs = list(col.find({"symbol": "BTCUSDT"}))
        rates = [d["rate"] for d in docs]
        assert pytest.approx(0.0001) in rates
        assert pytest.approx(-0.0002) in rates


class TestGetCollection:
    def test_get_collection_returns_collection(self, store):
        col = store.get_collection("market_data")
        assert col is not None

    def test_get_collection_custom_name(self, store):
        col = store.get_collection("custom_collection")
        col.insert_one({"key": "value"})
        assert col.count_documents({"key": "value"}) == 1