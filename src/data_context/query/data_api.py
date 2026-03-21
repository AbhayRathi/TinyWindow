"""Unified L1 data query API — the single interface for all downstream consumers."""

from __future__ import annotations
import pandas as pd
from typing import Optional

from data_context.storage.mongodb_store import MongoDBStore
from data_context.transform.indicators import IndicatorEngine
from data_context.transform.cleaner import DataCleaner


class DataAPI:
    """Single entry point for all L1 data access.

    Usage:
        api = DataAPI(store=MongoDBStore(config))
        df = api.get_ohlcv("AAPL", "2023-01-01", "2024-01-01", with_indicators=True)
    """

    def __init__(self, store: MongoDBStore):
        self._store = store
        self._indicators = IndicatorEngine()
        self._cleaner = DataCleaner()

    def get_ohlcv(
        self,
        symbol: str,
        start: str,
        end: str,
        timeframe: str = "1Day",
        with_indicators: bool = False,
        clean: bool = True,
    ) -> pd.DataFrame:
        """Query OHLCV from storage. Optionally clean and add indicators.

        Returns:
            DataFrame with DatetimeIndex and OHLCV columns
            (+ indicators if requested)
        """
        df = self._store.query_ohlcv(symbol, start, end)
        if df.empty:
            return df
        if clean:
            df = self._cleaner.deduplicate(df)
            df = self._cleaner.validate_ohlcv(df)
            df = self._cleaner.fill_gaps(df)
        if with_indicators:
            df = self._indicators.add_all(df)
        return df

    def get_sentiment(
        self,
        symbol: str,
        start: str,
        end: str,
        platform: Optional[str] = None,
    ) -> pd.DataFrame:
        """Query sentiment data from storage."""
        from datetime import datetime, timezone
        from pymongo import ASCENDING

        col = self._store.get_collection("sentiment_data")
        query: dict = {
            "symbol": symbol,
            "timestamp": {
                "$gte": datetime.fromisoformat(start).replace(tzinfo=timezone.utc),
                "$lte": datetime.fromisoformat(end).replace(tzinfo=timezone.utc),
            },
        }
        if platform:
            query["platform"] = platform
        docs = list(col.find(query).sort("timestamp", ASCENDING))
        if not docs:
            return pd.DataFrame()
        return pd.DataFrame(docs).drop(columns=["_id"], errors="ignore")

    def get_funding_rates(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        """Query perpetual futures funding rates."""
        from datetime import datetime, timezone
        from pymongo import ASCENDING

        col = self._store.get_collection("funding_rates")
        docs = list(
            col.find(
                {
                    "symbol": symbol,
                    "timestamp": {
                        "$gte": datetime.fromisoformat(start).replace(
                            tzinfo=timezone.utc
                        ),
                        "$lte": datetime.fromisoformat(end).replace(
                            tzinfo=timezone.utc
                        ),
                    },
                }
            ).sort("timestamp", ASCENDING)
        )
        if not docs:
            return pd.DataFrame()
        return pd.DataFrame(docs).drop(columns=["_id"], errors="ignore")
