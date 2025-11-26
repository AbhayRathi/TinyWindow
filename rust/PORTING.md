# Rust Porting Plan — MVP

Goal
- Port the encryption (PQC) primitives and a minimal execution adapter stub to Rust.
- Expose the encryption API to Python via PyO3/maturin as `tinywindow_rust_encryption`.

Scope (MVP)
- rust/encryption_service: deterministic keygen(seed), sign, verify APIs
- rust/exec_adapter_stub: async send_order / ack skeleton
- Python integration test to validate deterministic parity with Python baseline

Architecture Mapping
- Cross-cutting security / quantum/encryption layer → rust/encryption_service (PQC + signing/verification)
- Execution frontend / Layer 6 / exec_frontend → rust/exec_adapter_stub (low-latency order send/ack, pre-trade checks)
- Both crates integrate with telemetry and KMS/HSM boundaries
- Participate in system feedback loops (Layer 1..7)

API contract (Python-facing)
- key = keygen(seed: int) -> bytes
- sig = sign(key: bytes, payload: bytes) -> bytes
- ok = verify(key: bytes, payload: bytes, sig: bytes) -> bool

API contract (Rust)
```rust
// encryption_service
pub fn keygen(seed: u64) -> Vec<u8>
pub fn sign(key: &[u8], payload: &[u8]) -> Vec<u8>
pub fn verify(key: &[u8], payload: &[u8], sig: &[u8]) -> bool

// exec_adapter_stub
pub async fn send_order(order: Vec<u8>) -> Result<OrderAck, ExecError>
pub fn pre_trade_check(order: &[u8]) -> Result<(), ExecError>
```

Interop model
- Primary: PyO3 + maturin for in-process bindings (low-latency, simple CI).
- Fallback: gRPC server/client skeleton if in-process builds fail in CI.

## gRPC Fallback Proto Sketch

```protobuf
syntax = "proto3";
package tinywindow.encryption;

service EncryptionService {
  rpc Keygen(KeygenRequest) returns (KeygenResponse);
  rpc Sign(SignRequest) returns (SignResponse);
  rpc Verify(VerifyRequest) returns (VerifyResponse);
}

message KeygenRequest {
  uint64 seed = 1;
}

message KeygenResponse {
  bytes key = 1;
}

message SignRequest {
  bytes key = 1;
  bytes payload = 2;
}

message SignResponse {
  bytes signature = 1;
}

message VerifyRequest {
  bytes key = 1;
  bytes payload = 2;
  bytes signature = 3;
}

message VerifyResponse {
  bool valid = 1;
}
```

```protobuf
syntax = "proto3";
package tinywindow.execution;

service ExecutionAdapter {
  rpc SendOrder(SendOrderRequest) returns (OrderAck);
  rpc PreTradeCheck(PreTradeCheckRequest) returns (PreTradeCheckResponse);
}

message SendOrderRequest {
  bytes order_payload = 1;
}

message OrderAck {
  uint64 order_id = 1;
  bool accepted = 2;
  optional string reason = 3;
}

message PreTradeCheckRequest {
  bytes order_payload = 1;
}

message PreTradeCheckResponse {
  bool valid = 1;
  optional string reason = 2;
}
```

## KMS/HSM Contract

The encryption service is designed to integrate with external Key Management Systems (KMS) or Hardware Security Modules (HSM):

### Interface Contract
```rust
pub trait KeyProvider {
    /// Retrieve a key by identifier
    fn get_key(&self, key_id: &str) -> Result<Vec<u8>, KeyError>;
    
    /// Store a key with identifier
    fn store_key(&self, key_id: &str, key: &[u8]) -> Result<(), KeyError>;
    
    /// Delete a key by identifier
    fn delete_key(&self, key_id: &str) -> Result<(), KeyError>;
}

pub trait SecureSigner {
    /// Sign payload using HSM-protected key
    fn sign_secure(&self, key_id: &str, payload: &[u8]) -> Result<Vec<u8>, SignError>;
    
    /// Verify signature using HSM-protected key
    fn verify_secure(&self, key_id: &str, payload: &[u8], sig: &[u8]) -> Result<bool, VerifyError>;
}
```

### MVP Implementation
- For MVP, use in-memory deterministic key generation (seed-based)
- KMS integration is a future enhancement (see GitHub issues)
- HSM integration requires external crypto audit

### Future Integration Points
- AWS KMS / CloudHSM
- Azure Key Vault
- HashiCorp Vault
- Thales Luna HSM

## Telemetry Contract

Both crates emit structured telemetry for observability:

### Metrics
```
# Encryption Service
tinywindow_encryption_keygen_total{status="success|error"}
tinywindow_encryption_sign_total{status="success|error"}
tinywindow_encryption_verify_total{status="success|error",result="valid|invalid"}
tinywindow_encryption_latency_seconds{operation="keygen|sign|verify"}

# Execution Adapter
tinywindow_exec_orders_total{status="accepted|rejected"}
tinywindow_exec_order_latency_seconds{operation="send|pretrade"}
tinywindow_exec_errors_total{type="validation|connection|timeout"}
```

### Trace Spans
```
encryption.keygen (seed, key_size)
encryption.sign (key_size, payload_size)
encryption.verify (key_size, payload_size, sig_size)
exec.send_order (order_size, order_id)
exec.pre_trade_check (order_size)
```

### MVP Implementation
- For MVP, telemetry is structured logging to stdout
- Future: OpenTelemetry SDK integration
- Future: Prometheus metrics endpoint

## Threat Model Checklist

### Encryption Service Threats
- [ ] Key material exposure in memory (mitigation: zeroize on drop)
- [ ] Side-channel attacks on signing (mitigation: constant-time operations)
- [ ] Weak RNG (mitigation: use ChaCha20Rng with proper seeding)
- [ ] Replay attacks (mitigation: nonce/timestamp in payload)
- [ ] Key confusion (mitigation: domain separation in HMAC)

### Execution Adapter Threats
- [ ] Order injection (mitigation: signature verification on all orders)
- [ ] Order replay (mitigation: sequence numbers, timestamps)
- [ ] Denial of service (mitigation: rate limiting, pre-trade checks)
- [ ] Information leakage (mitigation: minimal error messages)
- [ ] Man-in-the-middle (mitigation: TLS for gRPC, in-process for PyO3)

### MVP Mitigations
- Use HMAC-SHA256 for deterministic signatures (placeholder)
- Validate all inputs before processing
- Return generic errors (don't leak internals)
- Log security-relevant events

### Post-MVP Security Tasks
- [ ] External crypto audit (liboqs integration)
- [ ] Penetration testing
- [ ] Fuzzing with cargo-fuzz
- [ ] Memory safety audit (Miri)

Determinism & Tests
- Functions must be deterministic given the same seed.
- Tests will use fixtures in `tests/fixtures/` and must not call external networks.
- Add failing Python integration test (tests/integration/test_rust_encryption_api.py) to define contract.

CI requirements
- cargo test for Rust crates
- cargo-audit (fail on high severity)
- maturin build & pip install wheel, then run Python integration tests against the wheel
- Keep existing Python CI for unit tests and coverage
- Optional: cargo-fuzz template job for future fuzzing

Security
- Use deterministic placeholder primitives for MVP (e.g., seed-based ed25519/HMAC) and document TODO to replace with liboqs or rust-oqs after crypto review.
- DO NOT ship PQC in production without an external crypto audit.

Next steps & issues
- Create GitHub issue: "Crypto audit: integrate liboqs & third-party review"
- Create GitHub issue: "Add cargo-fuzz harness for encryption inputs"
- Create GitHub issue: "KMS/HSM integration for production key management"
- After MVP: port exec/optimizer hot-paths incrementally, using same tests as acceptance criteria.

Acceptance criteria (for MVP PR)
- [x] Failing Python integration test added (defines contract).
- [x] Rust workspace created and unit tests added (cargo test).
- [x] PyO3 bindings built; Python integration test passes against the wheel.
- [ ] cargo-audit reports no high-severity findings.
- [x] rust/PORTING.md present and reviewed.
- [x] CI updated with Rust steps.

Notes
- DO NOT modify LICENSE or TDD_PLAN.md in this PR.
- Keep changes small, TDD-first, and well-documented.
