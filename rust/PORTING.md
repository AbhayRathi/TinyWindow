# Rust Porting Plan — MVP

Goal
- Port the encryption (PQC) primitives and a minimal execution adapter stub to Rust.
- Expose the encryption API to Python via PyO3/maturin as `tinywindow_rust_encryption`.

Scope (MVP)
- rust/encryption_service: deterministic keygen(seed), sign, verify APIs
- rust/exec_adapter_stub: async send_order / ack skeleton
- Python integration test to validate deterministic parity with Python baseline

API contract (Python-facing)
- key = keygen(seed: int) -> bytes
- sig = sign(key: bytes, payload: bytes) -> bytes
- ok = verify(key: bytes, payload: bytes, sig: bytes) -> bool

Interop model
- Primary: PyO3 + maturin for in-process bindings (low-latency, simple CI).
- Fallback: gRPC server/client skeleton if in-process builds fail in CI.

Determinism & Tests
- Functions must be deterministic given the same seed.
- Tests will use fixtures in `tests/fixtures/` and must not call external networks.
- Add failing Python integration test (tests/integration/test_rust_encryption_api.py) to define contract.

CI requirements
- cargo test for Rust crates
- cargo-audit (fail on high severity)
- maturin build & pip install wheel, then run Python integration tests against the wheel
- Keep existing Python CI for unit tests and coverage

Security
- Use deterministic placeholder primitives for MVP (e.g., seed-based ed25519/HMAC) and document TODO to replace with liboqs or rust-oqs after crypto review.
- DO NOT ship PQC in production without an external crypto audit.

Next steps & issues
- Create GitHub issue: "Crypto audit: integrate liboqs & third-party review"
- Create GitHub issue: "Add cargo-fuzz harness for encryption inputs"
- After MVP: port exec/optimizer hot-paths incrementally, using same tests as acceptance criteria.

Acceptance criteria (for MVP PR)
- Failing Python integration test added (defines contract).
- Rust workspace created and unit tests added (cargo test).
- PyO3 bindings built; Python integration test passes against the wheel.
- cargo-audit reports no high-severity findings.
- rust/PORTING.md present and reviewed.

Notes
- DO NOT modify LICENSE or TDD_PLAN.md in this PR.
- Keep changes small, TDD-first, and well-documented.
