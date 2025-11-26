//! Deterministic encryption primitives for TinyWindow.
//!
//! This crate provides deterministic keygen, sign, and verify functions
//! using HMAC-SHA256 as a placeholder for PQC primitives.
//!
//! # Security Warning
//! This is an MVP implementation using HMAC-based deterministic signatures.
//! TODO: Replace with liboqs/rust-oqs after external crypto audit.
//! DO NOT ship PQC in production without an external crypto audit.

use hmac::{Hmac, Mac};
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use rand::SeedableRng;
use rand_chacha::ChaCha20Rng;
use sha2::Sha256;

type HmacSha256 = Hmac<Sha256>;

/// Key size in bytes (256-bit key)
const KEY_SIZE: usize = 32;
/// Signature size in bytes (256-bit HMAC output)
const SIG_SIZE: usize = 32;

/// Generate a deterministic key from a seed.
///
/// Given the same seed, this function will always produce the same key.
/// This is essential for reproducible tests and deterministic behavior.
///
/// # Arguments
/// * `seed` - A 64-bit unsigned integer seed
///
/// # Returns
/// A 32-byte key as Vec<u8>
pub fn keygen(seed: u64) -> Vec<u8> {
    let mut rng = ChaCha20Rng::seed_from_u64(seed);
    let mut key = vec![0u8; KEY_SIZE];
    rand::Rng::fill(&mut rng, &mut key[..]);
    key
}

/// Sign a payload with the given key.
///
/// Uses HMAC-SHA256 for deterministic signatures.
/// Given the same key and payload, produces the same signature.
///
/// # Arguments
/// * `key` - The signing key (should be KEY_SIZE bytes)
/// * `payload` - The data to sign
///
/// # Returns
/// A 32-byte signature as Vec<u8>
pub fn sign(key: &[u8], payload: &[u8]) -> Vec<u8> {
    let mut mac =
        HmacSha256::new_from_slice(key).expect("HMAC can take key of any size");
    mac.update(payload);
    mac.finalize().into_bytes().to_vec()
}

/// Verify a signature against a payload using the given key.
///
/// # Arguments
/// * `key` - The verification key (same as signing key for HMAC)
/// * `payload` - The data that was signed
/// * `sig` - The signature to verify
///
/// # Returns
/// `true` if the signature is valid, `false` otherwise
pub fn verify(key: &[u8], payload: &[u8], sig: &[u8]) -> bool {
    let mut mac =
        HmacSha256::new_from_slice(key).expect("HMAC can take key of any size");
    mac.update(payload);
    mac.verify_slice(sig).is_ok()
}

// PyO3 bindings for Python interop
// These expose the encryption functions to Python as the `tinywindow_rust_encryption` module

/// Generate a deterministic key from a seed (Python binding).
#[pyfunction]
#[pyo3(name = "keygen")]
fn py_keygen<'py>(py: Python<'py>, seed: u64) -> Bound<'py, PyBytes> {
    let key = keygen(seed);
    PyBytes::new_bound(py, &key)
}

/// Sign a payload with the given key (Python binding).
#[pyfunction]
#[pyo3(name = "sign")]
fn py_sign<'py>(py: Python<'py>, key: Vec<u8>, payload: Vec<u8>) -> Bound<'py, PyBytes> {
    let sig = sign(&key, &payload);
    PyBytes::new_bound(py, &sig)
}

/// Verify a signature (Python binding).
#[pyfunction]
#[pyo3(name = "verify")]
fn py_verify(key: Vec<u8>, payload: Vec<u8>, sig: Vec<u8>) -> bool {
    verify(&key, &payload, &sig)
}

/// Python module for TinyWindow Rust encryption primitives.
#[pymodule]
fn tinywindow_rust_encryption(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(py_keygen, m)?)?;
    m.add_function(wrap_pyfunction!(py_sign, m)?)?;
    m.add_function(wrap_pyfunction!(py_verify, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_keygen_deterministic() {
        let seed = 42u64;
        let key1 = keygen(seed);
        let key2 = keygen(seed);
        assert_eq!(key1, key2, "keygen must be deterministic for the same seed");
        assert_eq!(key1.len(), KEY_SIZE);
    }

    #[test]
    fn test_keygen_different_seeds() {
        let key1 = keygen(42);
        let key2 = keygen(43);
        assert_ne!(key1, key2, "different seeds should produce different keys");
    }

    #[test]
    fn test_sign_deterministic() {
        let key = keygen(42);
        let payload = b"hello deterministic world";
        let sig1 = sign(&key, payload);
        let sig2 = sign(&key, payload);
        assert_eq!(sig1, sig2, "sign must be deterministic for the same key and payload");
        assert_eq!(sig1.len(), SIG_SIZE);
    }

    #[test]
    fn test_sign_verify_roundtrip() {
        let key = keygen(42);
        let payload = b"hello deterministic world";
        let sig = sign(&key, payload);
        assert!(verify(&key, payload, &sig), "verify should return true for valid signature");
    }

    #[test]
    fn test_verify_fails_with_wrong_key() {
        let key1 = keygen(42);
        let key2 = keygen(43);
        let payload = b"hello deterministic world";
        let sig = sign(&key1, payload);
        assert!(!verify(&key2, payload, &sig), "verify should fail with wrong key");
    }

    #[test]
    fn test_verify_fails_with_wrong_payload() {
        let key = keygen(42);
        let payload1 = b"hello deterministic world";
        let payload2 = b"different payload";
        let sig = sign(&key, payload1);
        assert!(!verify(&key, payload2, &sig), "verify should fail with wrong payload");
    }

    #[test]
    fn test_verify_fails_with_tampered_signature() {
        let key = keygen(42);
        let payload = b"hello deterministic world";
        let mut sig = sign(&key, payload);
        sig[0] ^= 0xff; // Tamper with signature
        assert!(!verify(&key, payload, &sig), "verify should fail with tampered signature");
    }
}
