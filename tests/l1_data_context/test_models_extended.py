"""Tests for extended L1 data models: SentimentData, TechnicalIndicators,
FundingRate, OrderBookSnapshot, NewsItem.
"""

import pytest
from data_context.models import (
    SentimentData,
    TechnicalIndicators,
    FundingRate,
    OrderBookSnapshot,
    NewsItem,
)


# ---------- SentimentData ----------


class TestSentimentData:
    def test_valid_construction(self):
        sd = SentimentData(
            timestamp=1700000000000,
            symbol="AAPL",
            platform="reddit",
            text="AAPL to the moon!",
            sentiment_score=0.85,
            source_url="https://reddit.com/r/stocks/123",
        )
        assert sd.symbol == "AAPL"
        assert sd.platform == "reddit"
        assert sd.sentiment_score == 0.85

    def test_valid_platforms(self):
        for platform in ("reddit", "twitter", "yahoo_news", "newsapi"):
            sd = SentimentData(
                timestamp=1700000000000,
                symbol="AAPL",
                platform=platform,
                text="test",
                sentiment_score=0.0,
            )
            assert sd.platform == platform

    def test_invalid_sentiment_score_too_high(self):
        with pytest.raises(ValueError, match="sentiment_score must be between"):
            SentimentData(
                timestamp=1700000000000,
                symbol="AAPL",
                platform="reddit",
                text="test",
                sentiment_score=1.5,
            )

    def test_invalid_sentiment_score_too_low(self):
        with pytest.raises(ValueError, match="sentiment_score must be between"):
            SentimentData(
                timestamp=1700000000000,
                symbol="AAPL",
                platform="reddit",
                text="test",
                sentiment_score=-1.5,
            )

    def test_invalid_platform(self):
        with pytest.raises(ValueError, match="Unknown platform"):
            SentimentData(
                timestamp=1700000000000,
                symbol="AAPL",
                platform="tiktok",
                text="test",
                sentiment_score=0.5,
            )

    def test_immutability(self):
        sd = SentimentData(
            timestamp=1700000000000,
            symbol="AAPL",
            platform="reddit",
            text="test",
            sentiment_score=0.5,
        )
        with pytest.raises(AttributeError):
            sd.symbol = "MSFT"

    def test_boundary_sentiment_scores(self):
        sd_min = SentimentData(
            timestamp=1, symbol="X", platform="reddit", text="t", sentiment_score=-1.0
        )
        sd_max = SentimentData(
            timestamp=1, symbol="X", platform="reddit", text="t", sentiment_score=1.0
        )
        assert sd_min.sentiment_score == -1.0
        assert sd_max.sentiment_score == 1.0


# ---------- TechnicalIndicators ----------


class TestTechnicalIndicators:
    def test_valid_construction_defaults(self):
        ti = TechnicalIndicators(timestamp=1700000000000, symbol="AAPL")
        assert ti.rsi is None
        assert ti.macd is None
        assert ti.obv is None

    def test_valid_construction_with_values(self):
        ti = TechnicalIndicators(
            timestamp=1700000000000,
            symbol="AAPL",
            rsi=65.3,
            macd=1.5,
            macd_signal=1.2,
            bb_upper=155.0,
            bb_lower=145.0,
            bb_mid=150.0,
            atr=2.5,
            vwap=150.5,
            obv=1000000.0,
        )
        assert ti.rsi == 65.3
        assert ti.bb_upper == 155.0

    def test_immutability(self):
        ti = TechnicalIndicators(timestamp=1, symbol="AAPL", rsi=50.0)
        with pytest.raises(AttributeError):
            ti.rsi = 60.0


# ---------- FundingRate ----------


class TestFundingRate:
    def test_valid_construction(self):
        fr = FundingRate(
            timestamp=1700000000000,
            symbol="BTCUSDT",
            rate=0.0001,
            exchange="binance",
        )
        assert fr.rate == 0.0001
        assert fr.exchange == "binance"

    def test_valid_exchanges(self):
        for exchange in ("binance", "bybit", "okx"):
            fr = FundingRate(
                timestamp=1, symbol="BTCUSDT", rate=0.0001, exchange=exchange
            )
            assert fr.exchange == exchange

    def test_invalid_exchange(self):
        with pytest.raises(ValueError, match="Unknown exchange"):
            FundingRate(timestamp=1, symbol="BTCUSDT", rate=0.0001, exchange="kraken")

    def test_immutability(self):
        fr = FundingRate(timestamp=1, symbol="BTCUSDT", rate=0.0001, exchange="binance")
        with pytest.raises(AttributeError):
            fr.rate = 0.0002


# ---------- OrderBookSnapshot ----------


class TestOrderBookSnapshot:
    def test_valid_construction(self):
        obs = OrderBookSnapshot(
            timestamp=1700000000000,
            symbol="BTCUSDT",
            bids=((50000.0, 1.5), (49999.0, 2.0)),
            asks=((50001.0, 1.0), (50002.0, 3.0)),
            mid_price=50000.5,
        )
        assert obs.mid_price == 50000.5
        assert len(obs.bids) == 2
        assert len(obs.asks) == 2

    def test_empty_book(self):
        obs = OrderBookSnapshot(
            timestamp=1,
            symbol="BTCUSDT",
            bids=(),
            asks=(),
            mid_price=50000.0,
        )
        assert obs.bids == ()
        assert obs.asks == ()

    def test_immutability(self):
        obs = OrderBookSnapshot(
            timestamp=1,
            symbol="BTCUSDT",
            bids=((50000.0, 1.0),),
            asks=((50001.0, 1.0),),
            mid_price=50000.5,
        )
        with pytest.raises(AttributeError):
            obs.mid_price = 50001.0


# ---------- NewsItem ----------


class TestNewsItem:
    def test_valid_construction(self):
        ni = NewsItem(
            timestamp=1700000000000,
            headline="Apple reports record earnings",
            source="bloomberg",
            sentiment_score=0.8,
            symbols=("AAPL",),
        )
        assert ni.headline == "Apple reports record earnings"
        assert ni.symbols == ("AAPL",)

    def test_default_symbols(self):
        ni = NewsItem(
            timestamp=1,
            headline="Market update",
            source="reuters",
            sentiment_score=0.0,
        )
        assert ni.symbols == ()

    def test_immutability(self):
        ni = NewsItem(
            timestamp=1,
            headline="Test",
            source="test",
            sentiment_score=0.0,
        )
        with pytest.raises(AttributeError):
            ni.headline = "Changed"
