"""Performance validation tests for Rust encryption."""

import pytest
import time


def test_encryption_sign_performance():
    """Benchmark sign performance - should handle >50k ops/sec."""
    tinywindow = pytest.importorskip("tinywindow_rust_encryption")
    
    key = tinywindow.keygen(42)
    payload = b"x" * 1024  # 1KB payload
    
    # Benchmark: 10k iterations of sign
    iterations = 10000
    start = time.time()
    for _ in range(iterations):
        tinywindow.sign(key, payload)
    elapsed = time.time() - start
    
    ops_per_sec = iterations / elapsed
    print(f"\nSign performance: {ops_per_sec:.0f} ops/sec (target: >50,000 ops/sec)")
    
    # Assert: >50k ops/sec
    assert ops_per_sec > 50000, f"Sign performance too slow: {ops_per_sec:.0f} ops/sec (expected >50,000)"


def test_encryption_latency_percentiles():
    """Measure latency percentiles for sign+verify operations."""
    tinywindow = pytest.importorskip("tinywindow_rust_encryption")
    
    key = tinywindow.keygen(42)
    payload = b"test payload"
    
    # Measure: 10k sign+verify operations
    iterations = 10000
    latencies = []
    
    for _ in range(iterations):
        start = time.perf_counter()
        sig = tinywindow.sign(key, payload)
        tinywindow.verify(key, payload, sig)
        elapsed = time.perf_counter() - start
        latencies.append(elapsed * 1_000_000)  # Convert to microseconds
    
    # Calculate percentiles
    latencies.sort()
    p50 = latencies[len(latencies) // 2]
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]
    
    print(f"\nLatency percentiles (sign+verify):")
    print(f"  P50: {p50:.2f}μs")
    print(f"  P95: {p95:.2f}μs")
    print(f"  P99: {p99:.2f}μs (target: <100μs)")
    
    # Assert: P99 < 100μs (financial trading requirement)
    assert p99 < 100, f"P99 latency too high: {p99:.2f}μs (expected <100μs)"
