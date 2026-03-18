"""Yahoo Finance data source adapter (yfinance)."""
import yfinance as yf
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential

from data_context.ingest.base import DataSource

INTERVAL_MAP = {
    "1Min": "1m",
    "5Min": "5m",
    "15Min": "15m",
    "1Hour": "1h",
    "1Day": "1d",
}


class YahooSource(DataSource):
    """Fetches OHLCV from Yahoo Finance via yfinance. No API key required."""

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
        interval = INTERVAL_MAP.get(timeframe, "1d")
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start, end=end, interval=interval)
        df = df[["Open", "High", "Low", "Close", "Volume"]]
        df.columns = ["open", "high", "low", "close", "volume"]
        df.index = pd.to_datetime(df.index, utc=True)
        df.index.name = "timestamp"
        return df.sort_index()
