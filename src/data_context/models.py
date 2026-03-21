"""Data models for L1 Data & Context layer."""

from dataclasses import dataclass
from typing import Tuple, Optional


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


@dataclass(frozen=True)
class SentimentData:
    """Immutable sentiment data point from social/news sources."""

    timestamp: int  # Unix epoch ms
    symbol: str
    platform: str  # e.g. "reddit", "twitter", "yahoo_news"
    text: str
    sentiment_score: float  # -1.0 to 1.0 (VADER compound)
    source_url: str = ""

    def __post_init__(self):
        if not -1.0 <= self.sentiment_score <= 1.0:
            raise ValueError("sentiment_score must be between -1.0 and 1.0")
        if self.platform not in {"reddit", "twitter", "yahoo_news", "newsapi"}:
            raise ValueError(f"Unknown platform: {self.platform}")


@dataclass(frozen=True)
class TechnicalIndicators:
    """Computed technical indicator snapshot for one symbol at one timestamp."""

    timestamp: int
    symbol: str
    rsi: Optional[float] = None  # 0–100
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_lower: Optional[float] = None
    bb_mid: Optional[float] = None
    atr: Optional[float] = None
    vwap: Optional[float] = None
    obv: Optional[float] = None  # On-Balance Volume


@dataclass(frozen=True)
class FundingRate:
    """Perpetual futures funding rate snapshot."""

    timestamp: int
    symbol: str
    rate: float  # e.g. 0.0001 = 0.01%
    exchange: str  # e.g. "binance"

    def __post_init__(self):
        if self.exchange not in {"binance", "bybit", "okx"}:
            raise ValueError(f"Unknown exchange: {self.exchange}")


@dataclass(frozen=True)
class OrderBookSnapshot:
    """Top-of-book snapshot."""

    timestamp: int
    symbol: str
    bids: Tuple[Tuple[float, float], ...]  # ((price, qty), ...)
    asks: Tuple[Tuple[float, float], ...]
    mid_price: float


@dataclass(frozen=True)
class NewsItem:
    """A single news headline with sentiment."""

    timestamp: int
    headline: str
    source: str
    sentiment_score: float  # -1.0 to 1.0
    symbols: Tuple[str, ...] = ()
