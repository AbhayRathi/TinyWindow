//! Logging configuration for TinyWindow telemetry.

use pyo3::prelude::*;

/// Setup logging with the specified level.
///
/// # Arguments
/// * `level` - Log level: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
///
/// # Errors
/// Returns `ValueError` if the level is invalid.
#[pyfunction]
pub fn setup_logging(level: &str) -> PyResult<()> {
    match level.to_uppercase().as_str() {
        "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL" => {
            // In a real implementation, this would configure env_logger or similar
            println!("Logging level set to: {}", level);
            Ok(())
        }
        _ => Err(pyo3::exceptions::PyValueError::new_err(format!(
            "Invalid logging level: {}. Must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL",
            level
        ))),
    }
}
