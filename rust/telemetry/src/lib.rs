//! Telemetry and metrics collection for TinyWindow.
//!
//! This crate provides Prometheus metrics and observability primitives
//! for TinyWindow's trading system with zero-overhead when not instrumented.
//!
//! # Features
//! - Counter metrics for events (e.g., orders_total)
//! - Histogram metrics for latency tracking (microseconds to seconds)
//! - Prometheus-compatible metrics export
//! - PyO3 bindings for Python integration

use lazy_static::lazy_static;
use prometheus::{Counter, Encoder, HistogramVec, Registry, TextEncoder};
use pyo3::prelude::*;

lazy_static! {
    static ref REGISTRY: Registry = Registry::new();
    static ref ORDERS_TOTAL: Counter =
        Counter::new("orders_total", "Total orders sent").unwrap();
    static ref LATENCY: HistogramVec = HistogramVec::new(
        prometheus::HistogramOpts::new("latency_seconds", "Operation latency")
            .buckets(vec![0.00001, 0.0001, 0.001, 0.01, 0.1]), // 10μs to 100ms
        &["operation"] // Add label for operation name
    )
    .unwrap();
}

/// Initialize metrics by registering them with the registry.
fn init_metrics() {
    static INIT: std::sync::Once = std::sync::Once::new();
    INIT.call_once(|| {
        REGISTRY
            .register(Box::new(ORDERS_TOTAL.clone()))
            .unwrap_or_else(|e| eprintln!("Failed to register ORDERS_TOTAL: {}", e));
        REGISTRY
            .register(Box::new(LATENCY.clone()))
            .unwrap_or_else(|e| eprintln!("Failed to register LATENCY: {}", e));
    });
}

/// Emit a metric by name.
///
/// Currently supports:
/// - "orders_total": Increments the total order counter
///
/// Note: Unknown metric names are silently ignored. This is intentional
/// to allow for flexible metric names without breaking existing code.
///
/// # Arguments
/// * `name` - The name of the metric
/// * `value` - The value (currently ignored for counters, reserved for future use)
pub fn emit_metric(name: &str, _value: f64) {
    init_metrics();
    if name == "orders_total" {
        ORDERS_TOTAL.inc();
    }
    // Silently ignore unknown metrics to allow for flexible metric names
}

/// Record operation latency.
///
/// Records latency with the operation name as a label, enabling per-operation filtering.
/// Operation names are validated to contain only alphanumeric characters and underscores
/// to prevent label injection attacks.
///
/// # Arguments
/// * `operation` - The name of the operation (e.g., "order_gen", "order_val")
/// * `duration_us` - The duration in microseconds
pub fn record_latency(operation: &str, duration_us: f64) {
    // Validate operation name to prevent label injection
    if !operation
        .chars()
        .all(|c| c.is_alphanumeric() || c == '_' || c == '.')
    {
        eprintln!("Invalid operation name: {}", operation);
        return;
    }

    init_metrics();
    LATENCY
        .with_label_values(&[operation])
        .observe(duration_us / 1_000_000.0); // Convert μs to seconds
}

/// Get Prometheus-formatted metrics.
///
/// # Returns
/// A string containing all metrics in Prometheus text format
///
/// # Note
/// This function uses unwrap() internally as encoding to a Vec<u8> and
/// converting to UTF-8 should never fail for Prometheus metrics output.
/// If it does fail, it indicates a serious internal error.
pub fn get_metrics() -> String {
    init_metrics();
    let mut buffer = Vec::new();
    let encoder = TextEncoder::new();
    let metric_families = REGISTRY.gather();
    encoder
        .encode(&metric_families, &mut buffer)
        .expect("Failed to encode metrics - this indicates a serious internal error");
    String::from_utf8(buffer).expect("Metrics should always be valid UTF-8")
}

// PyO3 bindings for Python interop

/// Emit a metric (Python binding).
#[pyfunction]
#[pyo3(name = "emit_metric")]
fn py_emit_metric(name: &str, value: f64) {
    emit_metric(name, value);
}

/// Record operation latency (Python binding).
#[pyfunction]
#[pyo3(name = "record_latency")]
fn py_record_latency(operation: &str, duration_us: f64) {
    record_latency(operation, duration_us);
}

/// Get Prometheus-formatted metrics (Python binding).
#[pyfunction]
#[pyo3(name = "get_metrics")]
fn py_get_metrics() -> String {
    get_metrics()
}

/// Python module for TinyWindow telemetry.
#[pymodule]
fn tinywindow_telemetry(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(py_emit_metric, m)?)?;
    m.add_function(wrap_pyfunction!(py_record_latency, m)?)?;
    m.add_function(wrap_pyfunction!(py_get_metrics, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_emit_metric() {
        emit_metric("orders_total", 1.0);
        let metrics = get_metrics();
        assert!(metrics.contains("orders_total"));
    }

    #[test]
    fn test_record_latency() {
        record_latency("test_op", 50.0); // 50μs
        let metrics = get_metrics();
        assert!(metrics.contains("latency_seconds"));
        assert!(metrics.contains(r#"operation="test_op""#));
    }

    #[test]
    fn test_per_operation_latency() {
        record_latency("order_gen", 50.0);
        record_latency("order_val", 100.0);
        let metrics = get_metrics();

        assert!(metrics.contains(r#"operation="order_gen""#));
        assert!(metrics.contains(r#"operation="order_val""#));
    }

    #[test]
    fn test_invalid_operation_name() {
        // Test with SQL injection attempt
        record_latency("test'; DROP TABLE--", 50.0);
        let metrics = get_metrics();

        // Should not contain the invalid operation
        assert!(!metrics.contains(r#"operation="test'; DROP TABLE--""#));
    }

    #[test]
    fn test_valid_operation_with_dots() {
        // Test that dots are allowed (common in operation names)
        record_latency("order.generation", 50.0);
        let metrics = get_metrics();

        assert!(metrics.contains(r#"operation="order.generation""#));
    }

    #[test]
    fn test_get_metrics_format() {
        emit_metric("orders_total", 1.0);
        let metrics = get_metrics();
        // Check that it's in Prometheus format
        assert!(metrics.contains("# HELP"));
        assert!(metrics.contains("# TYPE"));
    }
}
