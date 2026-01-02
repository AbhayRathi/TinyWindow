# TinyWindow Rust Components

**Mission**: Secure, high-performance crypto for financial system transformation.

## Architecture

- `encryption_service` → Cross-cutting Security (HMAC placeholder, PQC roadmap)
- `exec_adapter_stub` → Layer 6 Execution Frontend (<100μs latency)

## Development

```bash
cargo test --all               # Run Rust tests
maturin build --release        # Build Python wheel
pytest tests/integration/ -v   # Integration tests
```

## Security Warning

⚠️ **MVP uses HMAC-SHA256 (PQC placeholder). DO NOT ship without external audit.**

Roadmap: MVP → Audit → liboqs PQC → KMS/HSM → Production

## Performance Targets

- Keygen: >100k ops/sec
- Sign/Verify: >50k ops/sec
- P99: <100μs

## API

### Python Interface

```python
import tinywindow_rust_encryption

# Generate deterministic key from seed
key = tinywindow_rust_encryption.keygen(42)

# Sign payload
signature = tinywindow_rust_encryption.sign(key, b"payload")

# Verify signature
is_valid = tinywindow_rust_encryption.verify(key, b"payload", signature)
```

### Rust API

```rust
use encryption_service::{keygen, sign, verify};

// Generate key
let key = keygen(42);

// Sign payload
let sig = sign(&key, b"payload");

// Verify signature
let is_valid = verify(&key, b"payload", &sig);
```

## Building

### Prerequisites

- Rust 1.70+ (stable)
- Python 3.10+
- Maturin (`pip install maturin`)

### Build Python Wheel

```bash
cd rust
maturin build --release
pip install target/wheels/*.whl
```

### Development Build

```bash
cd rust
maturin develop  # Installs in development mode
```

## Testing

### Rust Unit Tests

```bash
cd rust
cargo test --all --verbose
```

### Python Integration Tests

```bash
# Build and install wheel first
cd rust && maturin build --release && pip install target/wheels/*.whl
cd ..

# Run tests
pytest tests/integration/test_rust_encryption_api.py -v
pytest tests/integration/test_rust_encryption_comprehensive.py -v
pytest tests/performance/ -v -s
```

## Linting & Formatting

```bash
cd rust

# Format code
cargo fmt --all

# Lint code
cargo clippy --all-targets --all-features -- -D warnings

# Security audit
cargo audit
```

## CI/CD

The CI pipeline runs:
1. Rust tests (`cargo test`)
2. Format check (`cargo fmt --check`)
3. Linting (`cargo clippy`)
4. Security audit (`cargo audit`)
5. Python wheel build (`maturin build`)
6. Integration tests (pytest)

## Architecture Details

### Encryption Service

- **Purpose**: Deterministic HMAC-SHA256 signing (PQC placeholder)
- **Exports**: Python module `tinywindow_rust_encryption`
- **Functions**:
  - `keygen(seed: int) -> bytes`: Generate 32-byte key
  - `sign(key: bytes, payload: bytes) -> bytes`: Generate 32-byte signature
  - `verify(key: bytes, payload: bytes, sig: bytes) -> bool`: Verify signature

**Determinism**: All operations are deterministic given the same seed, essential for:
- Reproducible tests
- Distributed consensus
- Audit trails

**Security Notes**:
- Uses ChaCha20 RNG with explicit seeding
- HMAC-SHA256 provides MAC (not encryption)
- Placeholder for post-quantum cryptography (PQC)
- Requires external audit before production use

### Execution Adapter Stub

- **Purpose**: Low-latency order send/ack skeleton
- **Target**: <100μs P99 latency
- **Functions**:
  - `send_order(order: Vec<u8>) -> Result<OrderAck, ExecError>`: Async order submission
  - `pre_trade_check(order: &[u8]) -> Result<(), ExecError>`: Pre-flight validation

**Architecture Mapping**:
- Maps to Layer 6 (Execution Frontend)
- Integrates with telemetry and KMS/HSM boundaries
- Participates in system feedback loops (L1-L7)

## Future Enhancements

See `PORTING.md` for detailed roadmap:

1. **Crypto Audit**: External review + liboqs integration
2. **KMS/HSM**: Production key management (AWS KMS, Azure Key Vault, etc.)
3. **Telemetry**: OpenTelemetry metrics and tracing
4. **Fuzzing**: cargo-fuzz harness for input validation
5. **gRPC Fallback**: Service interface if in-process binding fails

## Contributing

- Follow TDD: Write tests first
- Run `cargo fmt` before committing
- Ensure `cargo clippy` passes
- Add tests for new functionality
- Update documentation

## License

MIT - See LICENSE file
