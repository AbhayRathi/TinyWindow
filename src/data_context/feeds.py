"""Live data feed simulation."""

from datetime import datetime
from typing import Dict, Optional


class LiveFeed:
    """Live feed stub with staleness tracking."""

    def __init__(self, staleness_threshold_seconds: int):
        """Initialize live feed.

        Args:
            staleness_threshold_seconds: Time threshold for staleness
        """
        self.staleness_threshold_seconds = staleness_threshold_seconds
        self._data: Dict[str, float] = {}
        self._timestamps: Dict[str, datetime] = {}

    def update(self, symbol: str, price: float, timestamp: datetime):
        """Update feed with new data.

        Args:
            symbol: Trading symbol
            price: Current price
            timestamp: Data timestamp
        """
        self._data[symbol] = price
        self._timestamps[symbol] = timestamp

    def is_stale(self, symbol: str) -> bool:
        """Check if data for symbol is stale.

        Args:
            symbol: Trading symbol

        Returns:
            True if data is stale or missing
        """
        if symbol not in self._timestamps:
            return True

        age = datetime.now() - self._timestamps[symbol]
        return age.total_seconds() > self.staleness_threshold_seconds

    def get_last_update_time(self, symbol: str) -> Optional[datetime]:
        """Get last update time for symbol.

        Args:
            symbol: Trading symbol

        Returns:
            Last update timestamp or None
        """
        return self._timestamps.get(symbol)

    def get_staleness_metrics(self) -> Dict:
        """Get staleness metrics for all symbols.

        Returns:
            Dictionary with staleness statistics
        """
        total = len(self._timestamps)
        stale = sum(1 for symbol in self._timestamps if self.is_stale(symbol))
        fresh = total - stale

        return {
            "total_symbols": total,
            "stale_symbols": stale,
            "fresh_symbols": fresh,
            "stale_percentage": (stale / total * 100) if total > 0 else 0.0,
        }
