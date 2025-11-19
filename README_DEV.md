# TinyWindow - Developer Guide

## Getting Started

TinyWindow is a TDD-first AI trading system. Before making any changes, read [CONTRIBUTING.md](CONTRIBUTING.md) and [TDD_PLAN.md](TDD_PLAN.md).

## Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/AbhayRathi/TinyWindow.git
   cd TinyWindow
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   pip install -r requirements.txt
   ```

## Running Tests

### Run all tests:
```bash
pytest
```

### Run tests with coverage:
```bash
pytest --cov=. --cov-report=term-missing
```

### Check coverage threshold:
```bash
coverage report --fail-under=80
```

## Running CI Checks Locally

Before pushing, ensure all CI checks pass:

### 1. Linting:
```bash
# Check for errors
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Check for warnings
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

### 2. Run tests with coverage:
```bash
pytest --cov=. --cov-report=term-missing --cov-report=xml
coverage report --fail-under=80
```

## Project Structure

```
TinyWindow/
├── data_context/         # L1: Data ingestion and context
├── agents/               # L2: Market agents (futures, stocks, crypto, etc.)
├── retrain/              # L3: Retraining and optimization
├── qaqc_stage1/          # L4: Correctness and regression tests
├── qaqc_stage2/          # L5: Robustness and performance tests
├── strategy_opt/         # L6: Global strategy synthesis
├── exec_frontend/        # L7: Execution and frontend
├── quantum/              # Quantum utilities and mocks
├── onchain/              # Tokenization, vaults, DEX adapters
├── telemetry/            # Logging, metrics, traces
├── evaluation/           # PnL, risk, attribution
├── src/                  # Source code (scaffold from PR #1)
│   ├── core/
│   ├── data_ingestion/
│   ├── market_agents/
│   ├── optimization/
│   └── encryption/
├── tests/                # Test suite (28 test files)
├── .github/workflows/    # CI/CD pipelines
├── CONTRIBUTING.md       # Contribution guidelines
├── TDD_PLAN.md          # Milestone plan
└── README.md            # This file
```

## Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b tdd/m{N}-{description}
   ```

2. **Write tests FIRST** (TDD):
   - Create test file in `tests/`
   - Write failing test cases
   - Implement feature to make tests pass

3. **Run tests locally**:
   ```bash
   pytest --cov=. --cov-report=term-missing
   ```

4. **Lint your code**:
   ```bash
   flake8 .
   ```

5. **Push and create PR**:
   ```bash
   git push origin tdd/m{N}-{description}
   ```

6. **Ensure CI passes** before requesting review

## Milestones

See [TDD_PLAN.md](TDD_PLAN.md) for detailed milestone breakdown:

- **M0** (Current): Repo & CI setup
- **M1**: L1 Data/Context
- **M2**: L2 Agents
- **M3**: L3 Retraining
- **M4**: L4/L5 QAQC
- **M5**: L6 Strategy Optimization
- **M6**: L7 Execution
- **M7**: On-chain Alpha
- **M8**: RWA Alpha (Future)

## Key Principles

1. **TDD-Only**: Write tests before implementation
2. **100% Coverage**: Aim for complete test coverage (80% minimum for M0)
3. **Green CI**: All tests must pass
4. **No Leakage**: Strict data splits, no future information in training
5. **Determinism**: Fixed seeds, reproducible results

## Architecture

See [src/README.md](src/README.md) for detailed architecture documentation.

## Questions?

- Check [TDD_PLAN.md](TDD_PLAN.md) for milestone details
- Read [CONTRIBUTING.md](CONTRIBUTING.md) for workflow
- Review [src/README.md](src/README.md) for architecture
