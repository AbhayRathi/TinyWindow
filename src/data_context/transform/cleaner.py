"""Data cleaning utilities: outlier removal, gap filling, validation."""

import pandas as pd
import numpy as np


class DataCleaner:
    """Cleans OHLCV DataFrames before further processing."""

    def remove_outliers_zscore(
        self, df: pd.DataFrame, column: str, threshold: float = 3.5
    ) -> pd.DataFrame:
        """Replace values beyond `threshold` standard deviations with NaN."""
        df = df.copy()
        z = (df[column] - df[column].mean()) / df[column].std()
        df.loc[z.abs() > threshold, column] = np.nan
        return df

    def fill_gaps(self, df: pd.DataFrame, method: str = "ffill") -> pd.DataFrame:
        """Forward-fill (or back-fill) missing values."""
        df = df.copy()
        if method == "ffill":
            df = df.ffill()
        elif method == "bfill":
            df = df.bfill()
        elif method == "linear":
            df = df.interpolate(method="time")
        else:
            raise ValueError(f"Unknown fill method: {method}")
        return df

    def validate_ohlcv(self, df: pd.DataFrame) -> pd.DataFrame:
        """Drop rows where OHLCV constraints are violated (e.g. high < low)."""
        df = df.copy()
        invalid_mask = (
            (df["high"] < df["low"])
            | (df["close"] > df["high"])
            | (df["close"] < df["low"])
            | (df["open"] > df["high"])
            | (df["open"] < df["low"])
            | (df["volume"] < 0)
        )
        return df[~invalid_mask]

    def deduplicate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate timestamps, keeping the last entry."""
        return df[~df.index.duplicated(keep="last")]
