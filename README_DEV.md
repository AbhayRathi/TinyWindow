# TinyWindow Developer Guide

## Local Development Setup

### Prerequisites
- Python 3.10 or 3.11
- pip

### Initial Setup

1. Clone the repository:
```bash
git clone https://github.com/AbhayRathi/TinyWindow.git
cd TinyWindow
```

2. Install dependencies:
```bash
pip install -r requirements-dev.txt
pip install -e .
```

## Running Tests

### Run all tests:
```bash
pytest
```

### Run tests with coverage:
```bash
pytest --cov=src --cov-report=term-missing
```

### Run with coverage threshold (90%):
```bash
pytest --cov=src --cov-report=term-missing --cov-fail-under=90
```

### Run specific test file:
```bash
pytest tests/l1_data_context/test_schema_and_integrity.py -v
```

## Code Quality Checks

### Format code with black:
```bash
black .
```

### Check formatting:
```bash
black --check .
```

### Run flake8 linter:
```bash
flake8 src tests tools
```

### Run type checker:
```bash
mypy --ignore-missing-imports src
```

## CI Helper Tools

### Run smoke import tests:
```bash
python tools/smoke_imports.py
```

### Run determinism checks:
```bash
python tools/check_determinism.py
```

## Full CI Validation (Local)

To reproduce the full CI pipeline locally:

```bash
# 1. Format check
black --check .

# 2. Linting
flake8 src tests tools --count --select=E9,F63,F7,F82 --show-source --statistics

# 3. Type checking (optional)
mypy --ignore-missing-imports src || true

# 4. Smoke tests
python tools/smoke_imports.py

# 5. Determinism checks
python tools/check_determinism.py

# 6. Tests with coverage
pytest --cov=src --cov-report=term-missing --cov-fail-under=90
```

Or use this one-liner:
```bash
black --check . && \
flake8 src tests tools --count --select=E9,F63,F7,F82 --show-source --statistics && \
python tools/smoke_imports.py && \
python tools/check_determinism.py && \
pytest --cov=src --cov-report=term-missing --cov-fail-under=90
```

## TDD Workflow

TinyWindow follows strict TDD-first development:

1. **Write failing tests first**
   ```bash
   # Create test file
   touch tests/l1_data_context/test_new_feature.py
   # Write tests that fail
   pytest tests/l1_data_context/test_new_feature.py
   ```

2. **Implement minimal code to pass tests**
   ```bash
   # Edit implementation
   vim src/data_context/new_feature.py
   # Run tests
   pytest tests/l1_data_context/test_new_feature.py
   ```

3. **Refactor and validate**
   ```bash
   black .
   flake8 src tests
   pytest --cov=src --cov-fail-under=90
   ```

## Project Structure

```
TinyWindow/
├── src/                    # Source code
│   ├── data_context/       # L1: Data & Context
│   ├── agents/             # L2: Trading agents
│   ├── retrain/            # L3: Retraining
│   ├── qaqc_stage1/        # L4: QA/QC Stage 1
│   ├── qaqc_stage2/        # L5: QA/QC Stage 2
│   ├── strategy_opt/       # L6: Strategy optimization
│   ├── exec_frontend/      # L7: Execution & frontend
│   ├── quantum/            # Quantum utilities
│   ├── onchain/            # On-chain execution
│   ├── telemetry/          # Logging & monitoring
│   └── evaluation/         # PnL & risk evaluation
├── tests/                  # Test files
│   ├── l1_data_context/    # L1 tests
│   ├── fixtures/           # Golden test fixtures
│   └── ...
├── tools/                  # CI helper scripts
│   ├── check_determinism.py
│   └── smoke_imports.py
├── .github/workflows/      # GitHub Actions CI
└── docs/                   # Documentation
```

## Common Issues

### Import Errors
If you get "No module named 'src'" errors, make sure you've installed the package:
```bash
pip install -e .
```

### Coverage Below Threshold
The CI requires >= 90% coverage. Add tests for uncovered lines:
```bash
# Find uncovered lines
pytest --cov=src --cov-report=term-missing

# Look for "Missing" column to see which lines need tests
```

### Black Formatting Failures
Format your code before committing:
```bash
black .
```

## Contributing

See [TDD_PLAN.md](TDD_PLAN.md) for the overall development plan and milestones.

All contributions must:
- Follow TDD-first approach (tests before implementation)
- Maintain >= 90% code coverage
- Pass all linting and formatting checks
- Include deterministic tests with fixed seeds
- Not modify LICENSE or TDD_PLAN.md
