"""Telemetry layer for metrics and traces."""

import functools
import time
from typing import Callable

try:
    import tinywindow_telemetry as _rust_telemetry

    HAS_RUST = True
except ImportError:
    HAS_RUST = False


def emit_metric(name: str, value: float = 1.0) -> None:
    """Emit a metric (uses Rust if available, else no-op)."""
    if HAS_RUST:
        _rust_telemetry.emit_metric(name, value)


def track_latency(operation: str) -> Callable:
    """Decorator to track function latency in microseconds."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not HAS_RUST:
                return func(*args, **kwargs)

            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed_us = (time.perf_counter() - start) * 1_000_000
            _rust_telemetry.record_latency(operation, elapsed_us)
            return result

        return wrapper

    return decorator


def get_metrics() -> str:
    """Get Prometheus-formatted metrics."""
    if HAS_RUST:
        return _rust_telemetry.get_metrics()
    return "# Rust telemetry not available\n"
