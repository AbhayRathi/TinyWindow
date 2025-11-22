"""
L1 Data & Context: Schema and Integrity Tests

Tests schema contracts and data integrity for context objects.
"""

import pytest
import numpy as np


def test_market_context_schema():
    """Test that MarketContext has required fields."""
    from src.data_context.models import MarketContext

    # Create a simple context with minimal required fields
    context = MarketContext(
        timestamp=1234567890, symbol="AAPL", price=150.0, volume=1000000
    )

    assert context.timestamp == 1234567890
    assert context.symbol == "AAPL"
    assert context.price == 150.0
    assert context.volume == 1000000


def test_market_context_validation():
    """Test that MarketContext validates data types."""
    from src.data_context.models import MarketContext

    # Price must be positive
    with pytest.raises(ValueError, match="Price must be positive"):
        MarketContext(timestamp=1234567890, symbol="AAPL", price=-150.0, volume=1000000)

    # Volume must be non-negative
    with pytest.raises(ValueError, match="Volume must be non-negative"):
        MarketContext(timestamp=1234567890, symbol="AAPL", price=150.0, volume=-1000000)


def test_market_context_immutability():
    """Test that MarketContext is immutable after creation."""
    from src.data_context.models import MarketContext

    context = MarketContext(
        timestamp=1234567890, symbol="AAPL", price=150.0, volume=1000000
    )

    # Should not be able to modify fields
    with pytest.raises(AttributeError):
        context.price = 160.0


def test_data_snapshot_integrity():
    """Test that data snapshots maintain integrity."""
    from src.data_context.snapshot import DataSnapshot

    # Create snapshot with deterministic seed
    snapshot = DataSnapshot(seed=42)

    # Add some data
    data = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    snapshot.add_data("test_data", data)

    # Verify data integrity with hash
    assert snapshot.verify_integrity("test_data")

    # Modify external data should not affect snapshot (it stores a copy)
    data[0, 0] = 999.0
    assert snapshot.verify_integrity("test_data")  # Still valid

    # But if we corrupt internal data directly, integrity should fail
    snapshot._data["test_data"][0, 0] = 999.0
    assert not snapshot.verify_integrity("test_data")


def test_data_snapshot_deterministic():
    """Test that snapshots are deterministic with same seed."""
    from src.data_context.snapshot import DataSnapshot

    snapshot1 = DataSnapshot(seed=42)
    snapshot2 = DataSnapshot(seed=42)

    data = np.random.randn(10, 5)

    snapshot1.add_data("test", data.copy())
    snapshot2.add_data("test", data.copy())

    # Both should produce same hash
    assert snapshot1.get_hash("test") == snapshot2.get_hash("test")
