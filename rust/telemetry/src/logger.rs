//! Logging configuration for TinyWindow telemetry.

use pyo3::prelude::*;

/// Setup logging with the specified level.
///
/// # Arguments
/// * `level` - Log level: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
///
/// # Errors
/// Returns `ValueError` if the level is invalid.
///
/// # Note
/// This is a minimal implementation for M0. In production, this would integrate
/// with env_logger or a similar Rust logging framework. For now, it validates
/// the log level and prints a confirmation message.
#[pyfunction]
pub fn setup_logging(level: &str) -> PyResult<()> {
    match level.to_uppercase().as_str() {
        "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL" => {
            // Minimal implementation for M0 - validates level and confirms setup
            println!("Logging level set to: {}", level);
            Ok(())
        }
        _ => Err(pyo3::exceptions::PyValueError::new_err(format!(
            "Invalid logging level: {}. Must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL",
            level
        ))),
    }
}
