"""Tests for IndicatorEngine using synthetic OHLCV data (no API calls)."""

import numpy as np
import pandas as pd
import pytest

from data_context.transform.indicators import IndicatorEngine


@pytest.fixture
def ohlcv_df():
    """Create a synthetic OHLCV DataFrame with 100 rows."""
    np.random.seed(42)
    n = 100
    dates = pd.date_range("2023-01-01", periods=n, freq="D", tz="UTC")
    close = 100 + np.cumsum(np.random.randn(n) * 0.5)
    high = close + np.abs(np.random.randn(n))
    low = close - np.abs(np.random.randn(n))
    open_ = low + (high - low) * np.random.rand(n)
    volume = np.random.randint(1000, 100000, size=n).astype(float)

    df = pd.DataFrame(
        {
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        },
        index=dates,
    )
    df.index.name = "timestamp"
    return df


@pytest.fixture
def engine():
    return IndicatorEngine()


class TestAddRSI:
    def test_returns_rsi_column(self, engine, ohlcv_df):
        result = engine.add_rsi(ohlcv_df)
        assert "rsi" in result.columns

    def test_rsi_range(self, engine, ohlcv_df):
        result = engine.add_rsi(ohlcv_df)
        valid = result["rsi"].dropna()
        assert (valid >= 0).all() and (valid <= 100).all()

    def test_does_not_mutate_input(self, engine, ohlcv_df):
        original_cols = list(ohlcv_df.columns)
        engine.add_rsi(ohlcv_df)
        assert list(ohlcv_df.columns) == original_cols


class TestAddMACD:
    def test_returns_macd_columns(self, engine, ohlcv_df):
        result = engine.add_macd(ohlcv_df)
        assert "macd" in result.columns
        assert "macd_signal" in result.columns
        assert "macd_hist" in result.columns

    def test_does_not_mutate_input(self, engine, ohlcv_df):
        original_cols = list(ohlcv_df.columns)
        engine.add_macd(ohlcv_df)
        assert list(ohlcv_df.columns) == original_cols


class TestAddBollingerBands:
    def test_returns_bb_columns(self, engine, ohlcv_df):
        result = engine.add_bollinger_bands(ohlcv_df)
        assert "bb_upper" in result.columns
        assert "bb_mid" in result.columns
        assert "bb_lower" in result.columns

    def test_upper_above_lower(self, engine, ohlcv_df):
        result = engine.add_bollinger_bands(ohlcv_df)
        valid = result.dropna(subset=["bb_upper", "bb_lower"])
        assert (valid["bb_upper"] >= valid["bb_lower"]).all()


class TestAddATR:
    def test_returns_atr_column(self, engine, ohlcv_df):
        result = engine.add_atr(ohlcv_df)
        assert "atr" in result.columns

    def test_atr_non_negative(self, engine, ohlcv_df):
        result = engine.add_atr(ohlcv_df)
        valid = result["atr"].dropna()
        assert (valid >= 0).all()


class TestAddVWAP:
    def test_returns_vwap_column(self, engine, ohlcv_df):
        result = engine.add_vwap(ohlcv_df)
        assert "vwap" in result.columns


class TestAddOBV:
    def test_returns_obv_column(self, engine, ohlcv_df):
        result = engine.add_obv(ohlcv_df)
        assert "obv" in result.columns


class TestAddAll:
    def test_returns_all_expected_columns(self, engine, ohlcv_df):
        result = engine.add_all(ohlcv_df)
        expected = {
            "open",
            "high",
            "low",
            "close",
            "volume",
            "rsi",
            "macd",
            "macd_signal",
            "macd_hist",
            "bb_upper",
            "bb_mid",
            "bb_lower",
            "atr",
            "vwap",
            "obv",
        }
        assert expected.issubset(set(result.columns))


class TestSharpeRatio:
    def test_returns_float(self, engine):
        returns = pd.Series(np.random.randn(100) * 0.01)
        result = engine.sharpe_ratio(returns)
        assert isinstance(result, float)

    def test_zero_std_returns_zero(self, engine):
        returns = pd.Series([0.01] * 100)
        result = engine.sharpe_ratio(returns)
        assert result == 0.0

    def test_positive_returns_positive_sharpe(self, engine):
        returns = pd.Series([0.01] * 50 + [0.02] * 50)
        result = engine.sharpe_ratio(returns)
        assert result > 0


class TestMaxDrawdown:
    def test_returns_non_positive(self, engine):
        prices = pd.Series([100, 105, 103, 110, 95, 100])
        result = engine.max_drawdown(prices)
        assert result <= 0

    def test_monotonically_increasing_no_drawdown(self, engine):
        prices = pd.Series([100, 101, 102, 103, 104])
        result = engine.max_drawdown(prices)
        assert result == 0.0

    def test_known_drawdown(self, engine):
        prices = pd.Series([100, 50])
        result = engine.max_drawdown(prices)
        assert result == pytest.approx(-0.5)
