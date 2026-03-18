"""Abstract base class for all data sources."""
from abc import ABC, abstractmethod
import pandas as pd


class DataSource(ABC):
    """Abstract interface all ingest adapters must implement."""

    @abstractmethod
    def fetch_ohlcv(
        self,
        symbol: str,
        start: str,
        end: str,
        timeframe: str = "1Day",
    ) -> pd.DataFrame:
        """Return OHLCV DataFrame with columns: [open, high, low, close, volume].
        Index must be a tz-aware DatetimeIndex sorted ascending.
        """
        ...

    def name(self) -> str:
        return self.__class__.__name__
