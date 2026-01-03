"""Comprehensive integration tests for Rust encryption."""

import pytest


def test_rust_encryption_error_handling():
    """Test error handling in Rust encryption module."""
    tinywindow = pytest.importorskip("tinywindow_rust_encryption")

    # Test: wrong key verification fails
    key1 = tinywindow.keygen(42)
    key2 = tinywindow.keygen(43)
    payload = b"test payload"

    sig = tinywindow.sign(key1, payload)
    assert (
        tinywindow.verify(key2, payload, sig) is False
    ), "Signature with wrong key should fail"

    # Test: tampered signature fails
    sig_tampered = bytearray(sig)
    sig_tampered[0] ^= 0xFF
    assert (
        tinywindow.verify(key1, payload, bytes(sig_tampered)) is False
    ), "Tampered signature should fail"

    # Test: empty payloads work
    empty_payload = b""
    sig_empty = tinywindow.sign(key1, empty_payload)
    assert (
        tinywindow.verify(key1, empty_payload, sig_empty) is True
    ), "Empty payload should work"


def test_rust_encryption_edge_cases():
    """Test edge cases for Rust encryption."""
    tinywindow = pytest.importorskip("tinywindow_rust_encryption")

    key = tinywindow.keygen(42)

    # Test: empty payload
    empty = b""
    sig_empty = tinywindow.sign(key, empty)
    assert len(sig_empty) == 32, "Signature size should be constant (32 bytes)"
    assert tinywindow.verify(key, empty, sig_empty) is True

    # Test: single byte payload
    single = b"a"
    sig_single = tinywindow.sign(key, single)
    assert len(sig_single) == 32, "Signature size should be constant (32 bytes)"
    assert tinywindow.verify(key, single, sig_single) is True

    # Test: 1MB payload
    large = b"x" * (1024 * 1024)
    sig_large = tinywindow.sign(key, large)
    assert len(sig_large) == 32, "Signature size should be constant (32 bytes)"
    assert tinywindow.verify(key, large, sig_large) is True


def test_rust_encryption_security():
    """Test security properties of Rust encryption."""
    tinywindow = pytest.importorskip("tinywindow_rust_encryption")

    # Test: different payloads → different signatures
    key = tinywindow.keygen(42)
    payload1 = b"payload one"
    payload2 = b"payload two"
    sig1 = tinywindow.sign(key, payload1)
    sig2 = tinywindow.sign(key, payload2)
    assert sig1 != sig2, "Different payloads should produce different signatures"

    # Test: different seeds → different keys
    key1 = tinywindow.keygen(42)
    key2 = tinywindow.keygen(43)
    assert key1 != key2, "Different seeds should produce different keys"

    # Test: key isolation (sig from key1 fails with key2)
    key_a = tinywindow.keygen(100)
    key_b = tinywindow.keygen(200)
    payload = b"isolated test"
    sig_a = tinywindow.sign(key_a, payload)
    assert tinywindow.verify(key_a, payload, sig_a) is True
    assert (
        tinywindow.verify(key_b, payload, sig_a) is False
    ), "Signature should not verify with different key"

    # Test: entropy (>10 unique bytes per key)
    key = tinywindow.keygen(42)
    unique_bytes = len(set(key))
    assert unique_bytes > 10, f"Key should have >10 unique bytes, got {unique_bytes}"
