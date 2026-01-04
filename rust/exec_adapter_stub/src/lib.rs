//! Minimal async execution adapter stub for TinyWindow.
//!
//! This crate provides a skeleton for low-latency order send/ack operations
//! that will integrate with the execution frontend (Layer 6).
//!
//! # Architecture Mapping
//! - Maps to: Execution frontend / Layer 6 / exec_frontend
//! - Integrates with: telemetry and KMS/HSM boundaries
//! - Participates in: system feedback loops (Layer 1..7)

use std::sync::atomic::{AtomicU64, Ordering};

/// Order acknowledgment result
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct OrderAck {
    /// Unique order ID
    pub order_id: u64,
    /// Whether the order was accepted
    pub accepted: bool,
    /// Optional rejection reason
    pub reason: Option<String>,
}

/// Execution error types
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ExecError {
    /// Order validation failed
    ValidationFailed(String),
    /// Connection error
    ConnectionError(String),
    /// Timeout waiting for ack
    Timeout,
}

/// Counter for generating deterministic order IDs in tests
static ORDER_ID_COUNTER: AtomicU64 = AtomicU64::new(1);

/// Reset the order ID counter (for deterministic testing)
pub fn reset_order_id_counter() {
    ORDER_ID_COUNTER.store(1, Ordering::SeqCst);
}

/// Get the next order ID (deterministic within a test run)
fn next_order_id() -> u64 {
    ORDER_ID_COUNTER.fetch_add(1, Ordering::SeqCst)
}

/// Send an order asynchronously and receive an acknowledgment.
///
/// This is a stub implementation that provides a deterministic mock response
/// for testing purposes. In production, this would connect to the execution
/// frontend and perform actual order submission.
///
/// # Arguments
/// * `order` - The order payload as bytes
///
/// # Returns
/// * `Ok(OrderAck)` - Order acknowledgment with status
/// * `Err(ExecError)` - Error if order could not be processed
///
/// # Determinism
/// This function is deterministic for testing:
/// - Empty orders are rejected
/// - Non-empty orders are accepted with sequential IDs
pub async fn send_order(order: Vec<u8>) -> Result<OrderAck, ExecError> {
    // Validate order (stub: reject empty orders)
    if order.is_empty() {
        return Err(ExecError::ValidationFailed(
            "Order payload cannot be empty".to_string(),
        ));
    }

    // Simulate order processing (in production, this would be a real network call)
    // For MVP, we use a deterministic mock that always accepts valid orders
    let order_id = next_order_id();

    Ok(OrderAck {
        order_id,
        accepted: true,
        reason: None,
    })
}

/// Pre-trade check stub.
///
/// Validates an order before submission.
/// This is a placeholder for real pre-trade risk checks.
///
/// # Arguments
/// * `order` - The order payload as bytes
///
/// # Returns
/// * `Ok(())` - Order passes pre-trade checks
/// * `Err(ExecError)` - Order fails pre-trade checks
pub fn pre_trade_check(order: &[u8]) -> Result<(), ExecError> {
    if order.is_empty() {
        return Err(ExecError::ValidationFailed(
            "Order payload cannot be empty".to_string(),
        ));
    }
    // TODO: Add real pre-trade risk checks (position limits, margin checks, etc.)
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_send_order_accepts_valid_order() {
        let order = b"test order payload".to_vec();
        let result = send_order(order).await;
        assert!(result.is_ok());
        let ack = result.unwrap();
        assert!(ack.accepted);
        assert!(ack.order_id > 0); // IDs are positive and sequential
        assert!(ack.reason.is_none());
    }

    #[tokio::test]
    async fn test_send_order_rejects_empty_order() {
        let order = vec![];
        let result = send_order(order).await;
        assert!(result.is_err());
        match result.unwrap_err() {
            ExecError::ValidationFailed(msg) => {
                assert!(msg.contains("empty"));
            }
            _ => panic!("Expected ValidationFailed error"),
        }
    }

    #[tokio::test]
    async fn test_send_order_sequential_ids() {
        // Test that IDs are sequential (relative ordering)
        let order1 = b"order 1".to_vec();
        let order2 = b"order 2".to_vec();
        let order3 = b"order 3".to_vec();

        let ack1 = send_order(order1).await.unwrap();
        let ack2 = send_order(order2).await.unwrap();
        let ack3 = send_order(order3).await.unwrap();

        // Verify sequential ordering
        assert!(ack2.order_id > ack1.order_id);
        assert!(ack3.order_id > ack2.order_id);
    }

    #[test]
    fn test_pre_trade_check_valid_order() {
        let order = b"valid order";
        assert!(pre_trade_check(order).is_ok());
    }

    #[test]
    fn test_pre_trade_check_empty_order() {
        let order: &[u8] = &[];
        let result = pre_trade_check(order);
        assert!(result.is_err());
    }
}
