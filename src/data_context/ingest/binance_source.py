"""Binance data source adapter — spot OHLCV + perpetual funding rates."""
import pandas as pd
from binance.client import Client
from tenacity import retry, stop_after_attempt, wait_exponential

from data_context.config import BinanceConfig
from data_context.ingest.base import DataSource


INTERVAL_MAP = {
    "1Min": Client.KLINE_INTERVAL_1MINUTE,
    "5Min": Client.KLINE_INTERVAL_5MINUTE,
    "15Min": Client.KLINE_INTERVAL_15MINUTE,
    "1Hour": Client.KLINE_INTERVAL_1HOUR,
    "1Day": Client.KLINE_INTERVAL_1DAY,
}


class BinanceSource(DataSource):
    """Fetches crypto OHLCV and funding rates from Binance."""

    def __init__(self, config: BinanceConfig):
        self._client = Client(api_key=config.api_key, api_secret=config.api_secret)

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
        """Fetch spot OHLCV klines. Symbol e.g. 'BTCUSDT'."""
        interval = INTERVAL_MAP.get(timeframe, Client.KLINE_INTERVAL_1DAY)
        klines = self._client.get_historical_klines(symbol, interval, start, end)
        df = pd.DataFrame(
            klines,
            columns=[
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "close_time",
                "quote_volume",
                "trades",
                "taker_buy_base",
                "taker_buy_quote",
                "ignore",
            ],
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df = df.set_index("timestamp")
        df = df[["open", "high", "low", "close", "volume"]].astype(float)
        return df.sort_index()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def fetch_funding_rates(self, symbol: str, limit: int = 500) -> pd.DataFrame:
        """Fetch perpetual futures funding rate history.

        Returns:
            DataFrame with columns: [symbol, rate]
        """
        rates = self._client.futures_funding_rate(symbol=symbol, limit=limit)
        df = pd.DataFrame(rates)
        df["fundingTime"] = pd.to_datetime(df["fundingTime"], unit="ms", utc=True)
        df = df.rename(columns={"fundingTime": "timestamp", "fundingRate": "rate"})
        df["rate"] = df["rate"].astype(float)
        df = df.set_index("timestamp")[["symbol", "rate"]].sort_index()
        return df
