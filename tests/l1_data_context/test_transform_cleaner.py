"""Tests for DataCleaner utilities."""

import numpy as np
import pandas as pd
import pytest

from data_context.transform.cleaner import DataCleaner


@pytest.fixture
def cleaner():
    return DataCleaner()


@pytest.fixture
def ohlcv_df():
    """Create a simple OHLCV DataFrame for testing."""
    dates = pd.date_range("2023-01-01", periods=10, freq="D", tz="UTC")
    return pd.DataFrame(
        {
            "open": [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
            "high": [105, 106, 107, 108, 109, 110, 111, 112, 113, 114],
            "low": [95, 96, 97, 98, 99, 100, 101, 102, 103, 104],
            "close": [102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
            "volume": [
                1000,
                1100,
                1200,
                1300,
                1400,
                1500,
                1600,
                1700,
                1800,
                1900,
            ],
        },
        index=dates,
    )


class TestRemoveOutliersZscore:
    def test_replaces_outliers_with_nan(self, cleaner):
        df = pd.DataFrame({"close": [100, 101, 102, 103, 500, 101, 100, 102, 103, 99]})
        result = cleaner.remove_outliers_zscore(df, "close", threshold=2.0)
        assert result["close"].isna().any()
        # The outlier at index 4 (value=500) should be NaN
        assert pd.isna(result.loc[4, "close"])

    def test_no_outliers_unchanged(self, cleaner):
        df = pd.DataFrame({"close": [100, 101, 102, 103, 104]})
        result = cleaner.remove_outliers_zscore(df, "close", threshold=3.5)
        assert not result["close"].isna().any()

    def test_does_not_mutate_input(self, cleaner):
        df = pd.DataFrame({"close": [100, 101, 102, 103, 500]})
        original = df.copy()
        cleaner.remove_outliers_zscore(df, "close", threshold=2.0)
        pd.testing.assert_frame_equal(df, original)


class TestFillGaps:
    def test_ffill(self, cleaner):
        df = pd.DataFrame({"close": [100, np.nan, np.nan, 103, 104]})
        result = cleaner.fill_gaps(df, method="ffill")
        assert result["close"].tolist() == [100, 100, 100, 103, 104]

    def test_bfill(self, cleaner):
        df = pd.DataFrame({"close": [100, np.nan, np.nan, 103, 104]})
        result = cleaner.fill_gaps(df, method="bfill")
        assert result["close"].tolist() == [100, 103, 103, 103, 104]

    def test_invalid_method_raises(self, cleaner):
        df = pd.DataFrame({"close": [100, np.nan]})
        with pytest.raises(ValueError, match="Unknown fill method"):
            cleaner.fill_gaps(df, method="invalid")

    def test_does_not_mutate_input(self, cleaner):
        df = pd.DataFrame({"close": [100, np.nan, 102]})
        original = df.copy()
        cleaner.fill_gaps(df, method="ffill")
        pd.testing.assert_frame_equal(df, original)


class TestValidateOHLCV:
    def test_drops_invalid_rows(self, cleaner):
        dates = pd.date_range("2023-01-01", periods=3, freq="D", tz="UTC")
        df = pd.DataFrame(
            {
                "open": [100, 110, 100],
                "high": [105, 95, 105],  # row 1: high < low (invalid)
                "low": [95, 100, 95],
                "close": [102, 92, 102],
                "volume": [1000, 1000, 1000],
            },
            index=dates,
        )
        result = cleaner.validate_ohlcv(df)
        # Row 1 has high (95) < low (100) — should be dropped
        assert len(result) == 2

    def test_drops_negative_volume(self, cleaner):
        dates = pd.date_range("2023-01-01", periods=2, freq="D", tz="UTC")
        df = pd.DataFrame(
            {
                "open": [100, 100],
                "high": [105, 105],
                "low": [95, 95],
                "close": [102, 102],
                "volume": [1000, -1],
            },
            index=dates,
        )
        result = cleaner.validate_ohlcv(df)
        assert len(result) == 1

    def test_valid_data_unchanged(self, cleaner, ohlcv_df):
        result = cleaner.validate_ohlcv(ohlcv_df)
        assert len(result) == len(ohlcv_df)


class TestDeduplicate:
    def test_removes_duplicates(self, cleaner):
        dates = pd.to_datetime(
            ["2023-01-01", "2023-01-01", "2023-01-02"], utc=True
        )
        df = pd.DataFrame(
            {"close": [100, 101, 102]},
            index=dates,
        )
        result = cleaner.deduplicate(df)
        assert len(result) == 2
        # Should keep last entry for duplicate timestamp
        assert result.iloc[0]["close"] == 101

    def test_no_duplicates_unchanged(self, cleaner, ohlcv_df):
        result = cleaner.deduplicate(ohlcv_df)
        assert len(result) == len(ohlcv_df)
