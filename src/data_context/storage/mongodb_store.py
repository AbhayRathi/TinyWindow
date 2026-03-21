"""MongoDB Atlas storage adapter for L1 data."""

from __future__ import annotations
import pandas as pd
from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection
from typing import Optional

from data_context.config import MongoConfig


class MongoDBStore:
    """Stores and retrieves L1 data from MongoDB Atlas.

    Collections:
        - market_data: OHLCV bars
        - sentiment_data: scored sentiment records
        - funding_rates: perpetual futures funding rates
    """

    def __init__(self, config: MongoConfig):
        self._client = MongoClient(config.uri)
        self._db = self._client[config.db_name]
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create compound indexes for fast time-series queries."""
        self._db["market_data"].create_index(
            [("symbol", ASCENDING), ("timestamp", ASCENDING)], unique=True
        )
        self._db["sentiment_data"].create_index(
            [("symbol", ASCENDING), ("timestamp", ASCENDING)]
        )
        self._db["funding_rates"].create_index(
            [("symbol", ASCENDING), ("timestamp", ASCENDING)], unique=True
        )

    def upsert_ohlcv(self, df: pd.DataFrame, symbol: str, source: str):
        """Upsert OHLCV rows.

        df must have DatetimeIndex and [open,high,low,close,volume].
        """
        col: Collection = self._db["market_data"]
        docs = []
        for ts, row in df.iterrows():
            docs.append(
                {
                    "symbol": symbol,
                    "timestamp": ts.to_pydatetime(),
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": float(row["volume"]),
                    "source": source,
                }
            )
        for doc in docs:
            col.update_one(
                {"symbol": doc["symbol"], "timestamp": doc["timestamp"]},
                {"$set": doc},
                upsert=True,
            )

    def query_ohlcv(
        self,
        symbol: str,
        start: str,
        end: str,
    ) -> pd.DataFrame:
        """Return OHLCV DataFrame from MongoDB for symbol in [start, end]."""
        from datetime import datetime, timezone

        col: Collection = self._db["market_data"]
        cursor = col.find(
            {
                "symbol": symbol,
                "timestamp": {
                    "$gte": datetime.fromisoformat(start).replace(tzinfo=timezone.utc),
                    "$lte": datetime.fromisoformat(end).replace(tzinfo=timezone.utc),
                },
            }
        ).sort("timestamp", ASCENDING)
        docs = list(cursor)
        if not docs:
            return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
        df = pd.DataFrame(docs)
        df = df.set_index("timestamp")[["open", "high", "low", "close", "volume"]]
        df.index = pd.to_datetime(df.index, utc=True)
        return df

    def upsert_sentiment(self, df: pd.DataFrame):
        """Upsert sentiment records."""
        col: Collection = self._db["sentiment_data"]
        for _, row in df.iterrows():
            doc = row.to_dict()
            if hasattr(doc["timestamp"], "to_pydatetime"):
                doc["timestamp"] = doc["timestamp"].to_pydatetime()
            col.update_one(
                {
                    "source_url": doc.get("source_url", ""),
                    "timestamp": doc["timestamp"],
                },
                {"$set": doc},
                upsert=True,
            )

    def upsert_funding_rates(self, df: pd.DataFrame):
        """Upsert funding rate records."""
        col: Collection = self._db["funding_rates"]
        for ts, row in df.iterrows():
            doc = row.to_dict()
            doc["timestamp"] = (
                ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else ts
            )
            col.update_one(
                {"symbol": doc["symbol"], "timestamp": doc["timestamp"]},
                {"$set": doc},
                upsert=True,
            )

    def close(self):
        self._client.close()

    def get_collection(self, name: str) -> Collection:
        """Return a MongoDB collection by name."""
        return self._db[name]
