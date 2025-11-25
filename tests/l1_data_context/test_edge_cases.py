"""
Additional edge case tests for L1 Data & Context.

These tests cover previously untested error paths and edge cases.
"""

import pytest
import numpy as np


def test_feature_lookahead_not_implemented():
    """Test that lookahead feature engineering raises NotImplementedError."""
    from src.data_context.features import FeatureEngineer

    engineer = FeatureEngineer()
    prices = np.array([100, 101, 102, 103, 104])

    with pytest.raises(
        NotImplementedError, match="Lookahead calculation not implemented"
    ):
        engineer.calculate_returns(prices, lookahead=True)


def test_snapshot_verify_missing_key():
    """Test that verify_integrity returns False for missing key."""
    from src.data_context.snapshot import DataSnapshot

    snapshot = DataSnapshot(seed=42)

    # Verify non-existent key should return False
    assert not snapshot.verify_integrity("nonexistent_key")


def test_temporal_split_invalid_ratio():
    """Test that TemporalSplit validates train_ratio."""
    from src.data_context.splits import TemporalSplit

    # Ratio must be between 0 and 1
    with pytest.raises(ValueError, match="train_ratio must be between 0 and 1"):
        TemporalSplit(train_ratio=0.0)

    with pytest.raises(ValueError, match="train_ratio must be between 0 and 1"):
        TemporalSplit(train_ratio=1.0)

    with pytest.raises(ValueError, match="train_ratio must be between 0 and 1"):
        TemporalSplit(train_ratio=-0.5)

    with pytest.raises(ValueError, match="train_ratio must be between 0 and 1"):
        TemporalSplit(train_ratio=1.5)


def test_embargoed_split_mismatched_lengths():
    """Test that EmbargoedSplit validates input lengths."""
    from src.data_context.splits import EmbargoedSplit
    from datetime import datetime, timedelta

    splitter = EmbargoedSplit(train_ratio=0.7, embargo_days=7)

    dates = [datetime(2023, 1, 1) + timedelta(days=i) for i in range(100)]
    data = np.random.randn(50, 5)  # Mismatched length

    with pytest.raises(ValueError, match="dates and data must have same length"):
        splitter.split(dates, data)
