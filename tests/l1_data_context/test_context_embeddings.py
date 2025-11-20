"""
L1 Data & Context: Embedding Tests

Tests that embedding functions return deterministic vectors with fixed seed.
"""

import numpy as np


def test_embedding_deterministic_with_seed():
    """Test that embeddings are deterministic with fixed seed."""
    from src.data_context.embeddings import ContextEmbedder

    # Create embedder with fixed seed
    embedder1 = ContextEmbedder(seed=42, embedding_dim=128)
    embedder2 = ContextEmbedder(seed=42, embedding_dim=128)

    # Same input should produce same embedding
    input_data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

    emb1 = embedder1.embed(input_data)
    emb2 = embedder2.embed(input_data)

    assert emb1.shape == (128,)
    assert emb2.shape == (128,)
    assert np.allclose(emb1, emb2)


def test_embedding_shape():
    """Test that embeddings have correct shape."""
    from src.data_context.embeddings import ContextEmbedder

    embedder = ContextEmbedder(seed=42, embedding_dim=64)

    # Single sample
    input_data = np.array([1.0, 2.0, 3.0])
    emb = embedder.embed(input_data)
    assert emb.shape == (64,)

    # Batch of samples
    batch_data = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    batch_emb = embedder.embed_batch(batch_data)
    assert batch_emb.shape == (2, 64)


def test_embedding_different_seeds():
    """Test that different seeds produce different embeddings."""
    from src.data_context.embeddings import ContextEmbedder

    embedder1 = ContextEmbedder(seed=42, embedding_dim=128)
    embedder2 = ContextEmbedder(seed=123, embedding_dim=128)

    input_data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

    emb1 = embedder1.embed(input_data)
    emb2 = embedder2.embed(input_data)

    # Different seeds should produce different embeddings
    assert not np.allclose(emb1, emb2)


def test_embedding_normalization():
    """Test that embeddings are normalized."""
    from src.data_context.embeddings import ContextEmbedder

    embedder = ContextEmbedder(seed=42, embedding_dim=128, normalize=True)

    input_data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    emb = embedder.embed(input_data)

    # L2 norm should be 1.0
    norm = np.linalg.norm(emb)
    assert np.isclose(norm, 1.0)


def test_embedding_reproducibility():
    """Test that embeddings are reproducible across multiple calls."""
    from src.data_context.embeddings import ContextEmbedder

    embedder = ContextEmbedder(seed=42, embedding_dim=128)

    input_data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

    # Multiple calls should produce same result
    emb1 = embedder.embed(input_data)
    emb2 = embedder.embed(input_data)
    emb3 = embedder.embed(input_data)

    assert np.allclose(emb1, emb2)
    assert np.allclose(emb2, emb3)


def test_embedding_handles_different_input_sizes():
    """Test that embedder handles variable input sizes."""
    from src.data_context.embeddings import ContextEmbedder

    embedder = ContextEmbedder(seed=42, embedding_dim=64)

    # Different input sizes should all produce same output dimension
    small_input = np.array([1.0, 2.0])
    large_input = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])

    small_emb = embedder.embed(small_input)
    large_emb = embedder.embed(large_input)

    assert small_emb.shape == (64,)
    assert large_emb.shape == (64,)
