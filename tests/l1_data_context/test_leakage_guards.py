"""
L1 Data & Context: Leakage Guards Tests

Tests that train/test splits do not leak future information.
"""

import pytest
import numpy as np
from datetime import datetime, timedelta


def test_temporal_split_no_leakage():
    """Test that temporal split prevents future data leakage."""
    from src.data_context.splits import TemporalSplit

    # Create time series data
    dates = [datetime(2023, 1, 1) + timedelta(days=i) for i in range(100)]
    data = np.random.randn(100, 5)

    splitter = TemporalSplit(train_ratio=0.7)
    train_indices, test_indices = splitter.split(dates, data)

    # Train data should come before test data
    assert max([dates[i] for i in train_indices]) < min(
        [dates[i] for i in test_indices]
    )

    # No overlap between train and test
    assert len(set(train_indices) & set(test_indices)) == 0


def test_temporal_split_validation():
    """Test that temporal split validates inputs."""
    from src.data_context.splits import TemporalSplit

    splitter = TemporalSplit(train_ratio=0.7)

    # Mismatched lengths should raise error
    dates = [datetime(2023, 1, 1) + timedelta(days=i) for i in range(100)]
    data = np.random.randn(50, 5)  # Wrong length

    with pytest.raises(ValueError, match="dates and data must have same length"):
        splitter.split(dates, data)


def test_no_lookahead_bias_in_features():
    """Test that feature engineering doesn't use future data."""
    from src.data_context.features import FeatureEngineer

    # Create simple price series
    prices = np.array([100, 101, 102, 103, 104, 105])

    engineer = FeatureEngineer()

    # Calculate returns - should only use past data
    returns = engineer.calculate_returns(prices, lookahead=False)

    # First return should be NaN (no past data)
    assert np.isnan(returns[0])

    # Returns should be calculated from t-1 to t, not t to t+1
    assert returns[1] == pytest.approx((101 - 100) / 100)


def test_cross_validation_temporal_order():
    """Test that cross-validation maintains temporal order."""
    from src.data_context.splits import TimeSeriesCrossValidator

    dates = [datetime(2023, 1, 1) + timedelta(days=i) for i in range(100)]
    data = np.random.randn(100, 5)

    cv = TimeSeriesCrossValidator(n_splits=3)

    for train_idx, test_idx in cv.split(dates, data):
        # Each fold should maintain temporal order
        assert max([dates[i] for i in train_idx]) < min([dates[i] for i in test_idx])


def test_embargo_period():
    """Test that embargo period prevents information leakage."""
    from src.data_context.splits import EmbargoedSplit

    dates = [datetime(2023, 1, 1) + timedelta(days=i) for i in range(100)]
    data = np.random.randn(100, 5)

    # Use 7-day embargo period
    splitter = EmbargoedSplit(train_ratio=0.7, embargo_days=7)
    train_indices, test_indices = splitter.split(dates, data)

    # Gap between train and test should be at least 7 days
    gap = min([dates[i] for i in test_indices]) - max([dates[i] for i in train_indices])
    assert gap >= timedelta(days=7)
