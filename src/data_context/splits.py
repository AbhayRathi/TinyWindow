"""Data splitting utilities with leakage prevention."""

import numpy as np
from datetime import datetime
from typing import List, Tuple


class TemporalSplit:
    """Temporal train/test split that prevents future data leakage."""

    def __init__(self, train_ratio: float):
        """Initialize temporal splitter.

        Args:
            train_ratio: Fraction of data for training (0 < ratio < 1)
        """
        if not 0 < train_ratio < 1:
            raise ValueError("train_ratio must be between 0 and 1")
        self.train_ratio = train_ratio

    def split(
        self, dates: List[datetime], data: np.ndarray
    ) -> Tuple[List[int], List[int]]:
        """Split data temporally.

        Args:
            dates: List of datetime objects
            data: Data array

        Returns:
            Tuple of (train_indices, test_indices)
        """
        if len(dates) != len(data):
            raise ValueError("dates and data must have same length")

        # Sort by date
        sorted_indices = sorted(range(len(dates)), key=lambda i: dates[i])

        # Split point
        split_idx = int(len(dates) * self.train_ratio)

        train_indices = sorted_indices[:split_idx]
        test_indices = sorted_indices[split_idx:]

        return train_indices, test_indices


class EmbargoedSplit:
    """Temporal split with embargo period to prevent leakage."""

    def __init__(self, train_ratio: float, embargo_days: int):
        """Initialize embargoed splitter.

        Args:
            train_ratio: Fraction of data for training
            embargo_days: Number of days to exclude between train and test
        """
        self.train_ratio = train_ratio
        self.embargo_days = embargo_days

    def split(
        self, dates: List[datetime], data: np.ndarray
    ) -> Tuple[List[int], List[int]]:
        """Split data with embargo period.

        Args:
            dates: List of datetime objects
            data: Data array

        Returns:
            Tuple of (train_indices, test_indices)
        """
        if len(dates) != len(data):
            raise ValueError("dates and data must have same length")

        # Sort by date
        sorted_indices = sorted(range(len(dates)), key=lambda i: dates[i])

        # Find split point
        split_idx = int(len(dates) * self.train_ratio)

        # Find embargo cutoff
        train_end_date = dates[sorted_indices[split_idx - 1]]

        # Test starts after embargo period
        test_start_idx = split_idx
        from datetime import timedelta

        embargo_cutoff = train_end_date + timedelta(days=self.embargo_days)

        while (
            test_start_idx < len(dates)
            and dates[sorted_indices[test_start_idx]] < embargo_cutoff
        ):
            test_start_idx += 1

        train_indices = sorted_indices[:split_idx]
        test_indices = sorted_indices[test_start_idx:]

        return train_indices, test_indices


class TimeSeriesCrossValidator:
    """Cross-validation that maintains temporal order."""

    def __init__(self, n_splits: int):
        """Initialize cross-validator.

        Args:
            n_splits: Number of CV folds
        """
        self.n_splits = n_splits

    def split(self, dates: List[datetime], data: np.ndarray):
        """Generate train/test splits.

        Args:
            dates: List of datetime objects
            data: Data array

        Yields:
            Tuple of (train_indices, test_indices)
        """
        sorted_indices = sorted(range(len(dates)), key=lambda i: dates[i])
        n = len(dates)

        for i in range(self.n_splits):
            # Expanding window approach
            split_point = int(n * (i + 1) / (self.n_splits + 1))
            train_idx = sorted_indices[:split_point]

            # Test on next window
            test_start = split_point
            test_end = int(n * (i + 2) / (self.n_splits + 1))
            test_idx = sorted_indices[test_start:test_end]

            if len(test_idx) > 0:
                yield train_idx, test_idx
