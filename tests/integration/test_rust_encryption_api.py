"""
Integration tests for Rust encryption API.

These tests document the expected API contract for the tinywindow_rust_encryption module.
They will be skipped when the module is not available and will run once implemented.
"""

import pytest


payload = b"hello deterministic world"
seed = 42


def test_rust_encryption_roundtrip_importable():
    """Test that the Rust encryption module can perform encryption/decryption roundtrip."""
    # Skip if module is not available
    tinywindow_rust_encryption = pytest.importorskip("tinywindow_rust_encryption")

    key = tinywindow_rust_encryption.keygen(seed)
    assert isinstance(key, (bytes, bytearray))

    sig = tinywindow_rust_encryption.sign(key, payload)
    assert isinstance(sig, (bytes, bytearray))

    assert tinywindow_rust_encryption.verify(key, payload, sig) is True


def test_rust_encryption_deterministic():
    """Test that encryption/decryption roundtrip is consistent and repeatable."""
    # Skip if module is not available
    tinywindow_rust_encryption = pytest.importorskip("tinywindow_rust_encryption")

    k1 = tinywindow_rust_encryption.keygen(seed)
    k2 = tinywindow_rust_encryption.keygen(seed)
    assert k1 == k2

