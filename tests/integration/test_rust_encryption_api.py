"""
Integration tests for Rust encryption API.

These tests document the expected API contract for the tinywindow_rust_encryption module.
They will be skipped when the module is not available and will run once implemented.
"""

import pytest


def test_rust_encryption_roundtrip_importable():
    """Test that the Rust encryption module can perform encryption/decryption roundtrip."""
    # Skip if module is not available
    tinywindow_rust_encryption = pytest.importorskip("tinywindow_rust_encryption")

    # Test data
    plaintext = b"Hello, World!"
    key = b"test_key_32_bytes_long_for_aes"

    # Encrypt
    ciphertext = tinywindow_rust_encryption.encrypt(plaintext, key)

    # Verify ciphertext is different from plaintext
    assert ciphertext != plaintext
    assert len(ciphertext) > 0

    # Decrypt
    decrypted = tinywindow_rust_encryption.decrypt(ciphertext, key)

    # Verify roundtrip
    assert decrypted == plaintext


def test_rust_encryption_deterministic():
    """Test that encryption with same key and data produces consistent results."""
    # Skip if module is not available
    tinywindow_rust_encryption = pytest.importorskip("tinywindow_rust_encryption")

    # Test data
    plaintext = b"Deterministic test data"
    key = b"deterministic_key_for_testing"

    # Encrypt twice with same inputs
    ciphertext1 = tinywindow_rust_encryption.encrypt(plaintext, key)
    ciphertext2 = tinywindow_rust_encryption.encrypt(plaintext, key)

    # For deterministic encryption, results should be the same
    # Note: This assumes deterministic encryption. If using IV/nonce, this test may need adjustment
    assert ciphertext1 == ciphertext2

    # Both should decrypt to same plaintext
    decrypted1 = tinywindow_rust_encryption.decrypt(ciphertext1, key)
    decrypted2 = tinywindow_rust_encryption.decrypt(ciphertext2, key)

    assert decrypted1 == plaintext
    assert decrypted2 == plaintext
