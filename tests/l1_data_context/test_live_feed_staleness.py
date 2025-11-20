"""
L1 Data & Context: Live Feed Staleness Tests

Tests that feed stub reports staleness correctly.
"""

import pytest
from datetime import datetime, timedelta


def test_feed_staleness_threshold():
    """Test that feed correctly identifies stale data."""
    from src.data_context.feeds import LiveFeed

    feed = LiveFeed(staleness_threshold_seconds=5)

    # Add fresh data
    feed.update("AAPL", 150.0, datetime.now())

    # Should not be stale
    assert not feed.is_stale("AAPL")

    # Add old data
    old_timestamp = datetime.now() - timedelta(seconds=10)
    feed.update("MSFT", 300.0, old_timestamp)

    # Should be stale
    assert feed.is_stale("MSFT")


def test_feed_staleness_missing_symbol():
    """Test that missing symbols are reported as stale."""
    from src.data_context.feeds import LiveFeed

    feed = LiveFeed(staleness_threshold_seconds=5)

    # Symbol that was never updated should be stale
    assert feed.is_stale("NONEXISTENT")


def test_feed_last_update_time():
    """Test that feed tracks last update time correctly."""
    from src.data_context.feeds import LiveFeed

    feed = LiveFeed(staleness_threshold_seconds=5)

    timestamp = datetime.now()
    feed.update("AAPL", 150.0, timestamp)

    last_update = feed.get_last_update_time("AAPL")
    assert last_update == timestamp


def test_feed_staleness_recovery():
    """Test that stale feeds can become fresh again."""
    from src.data_context.feeds import LiveFeed

    feed = LiveFeed(staleness_threshold_seconds=5)

    # Add old data
    old_timestamp = datetime.now() - timedelta(seconds=10)
    feed.update("AAPL", 150.0, old_timestamp)

    assert feed.is_stale("AAPL")

    # Update with fresh data
    feed.update("AAPL", 151.0, datetime.now())

    assert not feed.is_stale("AAPL")


def test_feed_multiple_symbols():
    """Test staleness tracking for multiple symbols."""
    from src.data_context.feeds import LiveFeed

    feed = LiveFeed(staleness_threshold_seconds=5)

    now = datetime.now()
    old_time = now - timedelta(seconds=10)

    feed.update("AAPL", 150.0, now)
    feed.update("MSFT", 300.0, old_time)
    feed.update("GOOGL", 100.0, now)

    assert not feed.is_stale("AAPL")
    assert feed.is_stale("MSFT")
    assert not feed.is_stale("GOOGL")


def test_feed_staleness_metrics():
    """Test that feed provides staleness metrics."""
    from src.data_context.feeds import LiveFeed

    feed = LiveFeed(staleness_threshold_seconds=5)

    now = datetime.now()
    old_time = now - timedelta(seconds=10)

    feed.update("AAPL", 150.0, now)
    feed.update("MSFT", 300.0, old_time)
    feed.update("GOOGL", 100.0, now)

    metrics = feed.get_staleness_metrics()

    assert metrics["total_symbols"] == 3
    assert metrics["stale_symbols"] == 1
    assert metrics["fresh_symbols"] == 2
    assert metrics["stale_percentage"] == pytest.approx(33.33, rel=0.1)


def test_feed_configurable_threshold():
    """Test that staleness threshold is configurable."""
    from src.data_context.feeds import LiveFeed

    # Short threshold
    feed1 = LiveFeed(staleness_threshold_seconds=1)

    # Long threshold
    feed2 = LiveFeed(staleness_threshold_seconds=60)

    old_time = datetime.now() - timedelta(seconds=5)

    feed1.update("AAPL", 150.0, old_time)
    feed2.update("AAPL", 150.0, old_time)

    # Same data, different thresholds
    assert feed1.is_stale("AAPL")  # 5 seconds is stale with 1s threshold
    assert not feed2.is_stale("AAPL")  # 5 seconds is fresh with 60s threshold
