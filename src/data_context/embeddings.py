"""Context embedding utilities."""

import numpy as np


class ContextEmbedder:
    """Deterministic context embedder with fixed seed."""

    def __init__(self, seed: int, embedding_dim: int, normalize: bool = False):
        """Initialize embedder.

        Args:
            seed: Random seed for determinism
            embedding_dim: Dimension of output embeddings
            normalize: Whether to L2-normalize embeddings
        """
        self.seed = seed
        self.embedding_dim = embedding_dim
        self.normalize = normalize

        # Initialize random projection matrix deterministically
        rng = np.random.RandomState(seed)
        self.projection_matrix = rng.randn(1000, embedding_dim)  # Max input size 1000

    def embed(self, input_data: np.ndarray) -> np.ndarray:
        """Embed input data to fixed dimension.

        Args:
            input_data: Input array

        Returns:
            Embedded vector
        """
        # Pad or truncate to fixed size
        padded = np.zeros(self.projection_matrix.shape[0])
        padded[: min(len(input_data), len(padded))] = input_data[
            : min(len(input_data), len(padded))
        ]

        # Project to embedding dimension
        embedding = padded @ self.projection_matrix

        # Normalize if requested
        if self.normalize:
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm

        return embedding

    def embed_batch(self, batch_data: np.ndarray) -> np.ndarray:
        """Embed batch of inputs.

        Args:
            batch_data: Batch of input arrays (n_samples, n_features)

        Returns:
            Batch of embeddings (n_samples, embedding_dim)
        """
        return np.array([self.embed(row) for row in batch_data])
