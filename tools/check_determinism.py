#!/usr/bin/env python
"""
Check determinism of key components.

Validates that fixed seeds produce identical outputs for embeddings and snapshots.
"""
import sys
import os
import numpy as np

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_context.embeddings import ContextEmbedder
from src.data_context.snapshot import DataSnapshot


def check_embedder_determinism():
    """Verify embedder produces identical outputs with same seed."""
    print("Checking ContextEmbedder determinism...")

    embedder1 = ContextEmbedder(seed=42, embedding_dim=128)
    embedder2 = ContextEmbedder(seed=42, embedding_dim=128)

    test_data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

    emb1 = embedder1.embed(test_data)
    emb2 = embedder2.embed(test_data)

    if not np.allclose(emb1, emb2):
        print("❌ FAIL: Embedder not deterministic with same seed")
        return False

    # Multiple calls should be deterministic
    emb3 = embedder1.embed(test_data)
    if not np.allclose(emb1, emb3):
        print("❌ FAIL: Embedder not reproducible across multiple calls")
        return False

    print("✓ ContextEmbedder determinism verified")
    return True


def check_snapshot_integrity():
    """Verify snapshot integrity checking works."""
    print("Checking DataSnapshot integrity...")

    snapshot = DataSnapshot(seed=42)
    test_data = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])

    snapshot.add_data("test", test_data)

    # Verify integrity
    if not snapshot.verify_integrity("test"):
        print("❌ FAIL: Snapshot integrity check failed for valid data")
        return False

    # Corrupt data should fail
    snapshot._data["test"][0, 0] = 999.0
    if snapshot.verify_integrity("test"):
        print("❌ FAIL: Snapshot integrity check passed for corrupted data")
        return False

    print("✓ DataSnapshot integrity verification works")
    return True


def main():
    """Run all determinism checks."""
    print("=" * 60)
    print("Running determinism and integrity checks...")
    print("=" * 60)

    checks = [
        check_embedder_determinism(),
        check_snapshot_integrity(),
    ]

    if all(checks):
        print("\n✓ All determinism checks passed")
        return 0
    else:
        print("\n❌ Some determinism checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
