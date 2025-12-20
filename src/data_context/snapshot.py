"""Data snapshot with integrity checking."""

import hashlib
import numpy as np


class DataSnapshot:
    """Deterministic data snapshot with integrity verification."""

    def __init__(self, seed: int):
        """Initialize snapshot with random seed.

        Args:
            seed: Random seed for determinism
        """
        self.seed = seed
        self._data: dict[str, np.ndarray] = {}
        self._hashes: dict[str, str] = {}
        np.random.seed(seed)

    def add_data(self, key: str, data: np.ndarray):
        """Add data to snapshot and compute hash.

        Args:
            key: Data identifier
            data: Numpy array to store
        """
        # Store copy to prevent external modifications
        self._data[key] = data.copy()
        self._hashes[key] = self._compute_hash(data)

    def verify_integrity(self, key: str) -> bool:
        """Verify data integrity using stored hash.

        Args:
            key: Data identifier

        Returns:
            True if data matches stored hash
        """
        if key not in self._data or key not in self._hashes:
            return False

        current_hash = self._compute_hash(self._data[key])
        return current_hash == self._hashes[key]

    def get_hash(self, key: str) -> str:
        """Get stored hash for data.

        Args:
            key: Data identifier

        Returns:
            Hash string
        """
        return self._hashes.get(key, "")

    def _compute_hash(self, data: np.ndarray) -> str:
        """Compute SHA256 hash of numpy array.

        Args:
            data: Numpy array

        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(data.tobytes()).hexdigest()
