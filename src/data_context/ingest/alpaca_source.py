"""Alpaca Markets data source adapter."""
import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from tenacity import retry, stop_after_attempt, wait_exponential

from data_context.config import AlpacaConfig
from data_context.ingest.base import DataSource


TIMEFRAME_MAP = {
    "1Min": TimeFrame(1, TimeFrameUnit.Minute),
    "5Min": TimeFrame(5, TimeFrameUnit.Minute),
    "15Min": TimeFrame(15, TimeFrameUnit.Minute),
    "1Hour": TimeFrame(1, TimeFrameUnit.Hour),
    "1Day": TimeFrame(1, TimeFrameUnit.Day),
}


class AlpacaSource(DataSource):
    """Fetches US equity OHLCV from Alpaca Markets (free tier)."""

    def __init__(self, config: AlpacaConfig):
        self._client = StockHistoricalDataClient(
            api_key=config.api_key,
            secret_key=config.api_secret,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def fetch_ohlcv(
        self,
        symbol: str,
        start: str,
        end: str,
        timeframe: str = "1Day",
    ) -> pd.DataFrame:
        """Fetch OHLCV bars from Alpaca.

        Args:
            symbol: Ticker symbol, e.g. "AAPL"
            start: ISO date string, e.g. "2023-01-01"
            end: ISO date string, e.g. "2024-01-01"
            timeframe: One of "1Min","5Min","15Min","1Hour","1Day"

        Returns:
            DataFrame with DatetimeIndex and columns [open, high, low, close, volume]
        """
        from datetime import datetime

        tf = TIMEFRAME_MAP.get(timeframe, TimeFrame(1, TimeFrameUnit.Day))
        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=tf,
            start=datetime.fromisoformat(start),
            end=datetime.fromisoformat(end),
        )
        bars = self._client.get_stock_bars(request)
        df = bars.df
        if isinstance(df.index, pd.MultiIndex):
            df = df.xs(symbol, level="symbol")
        df = df[["open", "high", "low", "close", "volume"]].sort_index()
        return df
