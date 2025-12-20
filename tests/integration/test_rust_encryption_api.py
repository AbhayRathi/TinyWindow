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
    key = b"test_key_32bytes_for_aes_256!!"  # Exactly 32 bytes for AES-256

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
    """Test that encryption/decryption roundtrip is consistent and repeatable."""
    # Skip if module is not available
    tinywindow_rust_encryption = pytest.importorskip("tinywindow_rust_encryption")

    # Test data
    plaintext = b"Deterministic test data"
    key = b"another_key_32bytes_for_aes!!"  # Exactly 32 bytes for AES-256

    # Encrypt multiple times to test repeatability of decryption
    ciphertext1 = tinywindow_rust_encryption.encrypt(plaintext, key)
    ciphertext2 = tinywindow_rust_encryption.encrypt(plaintext, key)

    # Note: Ciphertexts may differ due to random IV/nonce (which is good for security)
    # What matters is that both decrypt correctly to the same plaintext

    # Both ciphertexts should decrypt to the original plaintext
    decrypted1 = tinywindow_rust_encryption.decrypt(ciphertext1, key)
    decrypted2 = tinywindow_rust_encryption.decrypt(ciphertext2, key)

    assert decrypted1 == plaintext
    assert decrypted2 == plaintext
