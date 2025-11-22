"""Feature engineering utilities."""

import numpy as np


class FeatureEngineer:
    """Feature engineering with leakage prevention."""

    def calculate_returns(
        self, prices: np.ndarray, lookahead: bool = False
    ) -> np.ndarray:
        """Calculate returns from price series.

        Args:
            prices: Array of prices
            lookahead: If False, prevents lookahead bias

        Returns:
            Array of returns
        """
        if lookahead:
            raise NotImplementedError("Lookahead calculation not implemented")

        returns = np.zeros(len(prices))
        returns[0] = np.nan  # No past data for first point

        for i in range(1, len(prices)):
            returns[i] = (prices[i] - prices[i - 1]) / prices[i - 1]

        return returns
