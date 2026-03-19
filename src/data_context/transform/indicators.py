"""Technical indicator computation using pandas-ta."""
import pandas as pd
import pandas_ta_classic as ta


class IndicatorEngine:
    """Computes standard technical indicators on OHLCV DataFrames.

    All methods accept a DataFrame with columns [open, high, low, close, volume]
    and return a new DataFrame with indicator columns appended.
    No lookahead bias: all indicators use only past data (pandas-ta default).
    """

    def add_rsi(self, df: pd.DataFrame, length: int = 14) -> pd.DataFrame:
        df = df.copy()
        df["rsi"] = ta.rsi(df["close"], length=length)
        return df

    def add_macd(
        self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> pd.DataFrame:
        df = df.copy()
        macd = ta.macd(df["close"], fast=fast, slow=slow, signal=signal)
        df["macd"] = macd[f"MACD_{fast}_{slow}_{signal}"]
        df["macd_signal"] = macd[f"MACDs_{fast}_{slow}_{signal}"]
        df["macd_hist"] = macd[f"MACDh_{fast}_{slow}_{signal}"]
        return df

    def add_bollinger_bands(
        self, df: pd.DataFrame, length: int = 20, std: float = 2.0
    ) -> pd.DataFrame:
        df = df.copy()
        bb = ta.bbands(df["close"], length=length, std=std)
        # pandas-ta column names vary by version; find them dynamically
        bb_cols = bb.columns.tolist()
        bbl = [c for c in bb_cols if c.startswith("BBL_")][0]
        bbm = [c for c in bb_cols if c.startswith("BBM_")][0]
        bbu = [c for c in bb_cols if c.startswith("BBU_")][0]
        df["bb_lower"] = bb[bbl]
        df["bb_mid"] = bb[bbm]
        df["bb_upper"] = bb[bbu]
        return df

    def add_atr(self, df: pd.DataFrame, length: int = 14) -> pd.DataFrame:
        df = df.copy()
        df["atr"] = ta.atr(df["high"], df["low"], df["close"], length=length)
        return df

    def add_vwap(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["vwap"] = ta.vwap(df["high"], df["low"], df["close"], df["volume"])
        return df

    def add_obv(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["obv"] = ta.obv(df["close"], df["volume"])
        return df

    def add_all(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all indicators at once."""
        df = self.add_rsi(df)
        df = self.add_macd(df)
        df = self.add_bollinger_bands(df)
        df = self.add_atr(df)
        df = self.add_vwap(df)
        df = self.add_obv(df)
        return df

    def sharpe_ratio(
        self,
        returns: pd.Series,
        risk_free_rate: float = 0.0,
        periods_per_year: int = 252,
    ) -> float:
        """Compute annualized Sharpe ratio from a returns series."""
        excess = returns - risk_free_rate / periods_per_year
        std = excess.std()
        if std < 1e-10:
            return 0.0
        return float((excess.mean() / std) * (periods_per_year**0.5))

    def max_drawdown(self, prices: pd.Series) -> float:
        """Compute maximum drawdown from a price series. Returns negative float."""
        cummax = prices.cummax()
        drawdown = (prices - cummax) / cummax
        return float(drawdown.min())
