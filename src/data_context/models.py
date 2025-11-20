"""Data models for L1 Data & Context layer."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MarketContext:
    """Immutable market context data."""

    timestamp: int
    symbol: str
    price: float
    volume: int

    def __post_init__(self):
        """Validate fields after initialization."""
        if self.price <= 0:
            raise ValueError("Price must be positive")
        if self.volume < 0:
            raise ValueError("Volume must be non-negative")
