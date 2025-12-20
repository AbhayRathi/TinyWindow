import hashlib
import numpy as np
from typing import Optional


class Snapshot:
    """
    A snapshot represents the state of data at a particular point in time.
    It stores data arrays and their corresponding hashes for integrity verification.
    """

    def __init__(self, name: str):
        """
        Initialize a new snapshot with the given name.
        """
        self.name = name
        self._data: dict[str, np.ndarray] = {}
        self._hashes: dict[str, str] = {}

    def add_data(self, key: str, data: np.ndarray) -> None:
        """
        Add data to the snapshot with a unique key.
        """
        self._data[key] = data
        self._hashes[key] = self._compute_hash(data)

    def get_data(self, key: str) -> Optional[np.ndarray]:
        """
        Retrieve data from the snapshot by key.
        """
        return self._data.get(key)

    def verify_integrity(self, key: str) -> bool:
        """
        Verify that the data for the given key has not been modified.
        """
        if key not in self._data or key not in self._hashes:
            return False
        return self._hashes[key] == self._compute_hash(self._data[key])

    def _compute_hash(self, data: np.ndarray) -> str:
        """
        Compute a hash for the given numpy array.
        """
        return hashlib.sha256(data.tobytes()).hexdigest()

    def __repr__(self) -> str:
        return f"Snapshot(name='{self.name}', keys={list(self._data.keys())})"
