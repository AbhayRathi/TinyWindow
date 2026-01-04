"""
Integration tests for Rust telemetry API.

These tests document the expected API contract for the tinywindow_telemetry module.
They will be skipped when the module is not available and will run once built.
"""

import logging
import time

import pytest


def test_telemetry_metrics():
    """Test that telemetry metrics can be emitted and retrieved."""
    telemetry = pytest.importorskip("tinywindow_telemetry")

    # Emit metrics
    telemetry.emit_metric("orders_total", 1.0)
    telemetry.record_latency("test_op", 50.0)  # 50μs

    # Get Prometheus output
    metrics = telemetry.get_metrics()
    assert "orders_total" in metrics
    assert "latency_seconds" in metrics


def test_python_decorator():
    """Test that the Python @track_latency decorator works."""
    from src.telemetry import track_latency

    @track_latency("test_function")
    def slow_function():
        time.sleep(0.001)  # 1ms

    slow_function()  # Should record ~1000μs latency


def test_python_emit_metric():
    """Test that the Python emit_metric wrapper works."""
    from src.telemetry import emit_metric

    # Should not raise even if Rust module is not available
    emit_metric("orders_total", 1.0)


def test_python_get_metrics():
    """Test that the Python get_metrics wrapper works."""
    from src.telemetry import get_metrics

    metrics = get_metrics()
    assert isinstance(metrics, str)
    # If Rust is available, should have proper format
    # If not, should return fallback message


def test_rust_metrics_format():
    """Test that metrics are in proper Prometheus format."""
    telemetry = pytest.importorskip("tinywindow_telemetry")

    telemetry.emit_metric("orders_total", 1.0)
    metrics = telemetry.get_metrics()

    # Check Prometheus format
    assert "# HELP" in metrics or "# TYPE" in metrics
    assert "orders_total" in metrics


def test_rust_latency_recording():
    """Test that latency can be recorded and retrieved."""
    telemetry = pytest.importorskip("tinywindow_telemetry")

    # Record various latencies
    telemetry.record_latency("op1", 10.0)  # 10μs
    telemetry.record_latency("op2", 100.0)  # 100μs
    telemetry.record_latency("op3", 1000.0)  # 1ms

    metrics = telemetry.get_metrics()
    assert "latency_seconds" in metrics


def test_per_operation_latency_labels():
    """Test that latency tracking includes operation labels for filtering."""
    telemetry = pytest.importorskip("tinywindow_telemetry")

    # Record latencies for different operations
    telemetry.record_latency("order_gen", 50.0)
    telemetry.record_latency("order_val", 100.0)
    telemetry.record_latency("order_gen", 75.0)  # Second measurement for order_gen

    metrics = telemetry.get_metrics()

    # Verify per-operation labels exist
    assert 'operation="order_gen"' in metrics
    assert 'operation="order_val"' in metrics

    # Verify counts are correct (order_gen should have 2 samples)
    assert 'latency_seconds_count{operation="order_gen"} 2' in metrics
    assert 'latency_seconds_count{operation="order_val"} 1' in metrics


def test_invalid_operation_names_rejected():
    """Test that invalid operation names are rejected to prevent injection."""
    telemetry = pytest.importorskip("tinywindow_telemetry")

    # Test with SQL injection attempt
    telemetry.record_latency("test'; DROP TABLE--", 50.0)

    metrics = telemetry.get_metrics()

    # Should not contain the invalid operation
    assert 'operation="test\'; DROP TABLE--"' not in metrics


def test_valid_operation_names_with_dots():
    """Test that operation names with dots are allowed (common pattern)."""
    telemetry = pytest.importorskip("tinywindow_telemetry")

    # Test with dots (common in hierarchical operation names)
    telemetry.record_latency("order.generation", 50.0)

    metrics = telemetry.get_metrics()

    # Should contain the operation with dots
    assert 'operation="order.generation"' in metrics


def test_logger_setup():
    """Test that the logger setup works."""
    from src.telemetry.logger import setup_logging

    # Test with different levels - the function should not raise
    setup_logging("INFO")
    setup_logging("DEBUG")
    setup_logging("WARNING")

    # Test invalid level raises ValueError
    try:
        setup_logging("INVALID_LEVEL")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Invalid logging level" in str(e)
