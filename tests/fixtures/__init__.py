"""Golden test fixtures for deterministic testing."""

import numpy as np
import json
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent


def get_golden_embeddings():
    """Get golden embedding test data."""
    return {
        "seed": 42,
        "input_data": np.array([1.0, 2.0, 3.0, 4.0, 5.0]),
        "embedding_dim": 128,
    }


def get_golden_price_series():
    """Get golden price series for testing."""
    return np.array([100.0, 101.0, 102.0, 103.0, 104.0, 105.0])


def get_golden_market_data():
    """Get golden market data for testing."""
    return {
        "timestamp": 1234567890,
        "symbol": "AAPL",
        "price": 150.0,
        "volume": 1000000,
    }


def save_golden_embedding_result(embedder_output, filename="golden_embedding.npy"):
    """Save golden embedding result for validation."""
    filepath = FIXTURES_DIR / filename
    np.save(filepath, embedder_output)


def load_golden_embedding_result(filename="golden_embedding.npy"):
    """Load golden embedding result."""
    filepath = FIXTURES_DIR / filename
    if filepath.exists():
        return np.load(filepath)
    return None
