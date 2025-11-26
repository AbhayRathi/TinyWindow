import pytest

payload = b"hello deterministic world"
seed = 42

def test_rust_encryption_roundtrip_importable():
    # This test defines the contract; it will fail until tinywindow_rust_encryption is implemented.
    import tinywindow_rust_encryption

    key = tinywindow_rust_encryption.keygen(seed)
    assert isinstance(key, (bytes, bytearray))

    sig = tinywindow_rust_encryption.sign(key, payload)
    assert isinstance(sig, (bytes, bytearray))

    assert tinywindow_rust_encryption.verify(key, payload, sig) is True

def test_rust_encryption_deterministic():
    import tinywindow_rust_encryption
    k1 = tinywindow_rust_encryption.keygen(seed)
    k2 = tinywindow_rust_encryption.keygen(seed)
    assert k1 == k2
