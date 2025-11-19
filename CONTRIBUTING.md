# Contributing to TinyWindow

## TDD-First Policy

TinyWindow follows strict Test-Driven Development (TDD) practices:

1. **Write tests first** - All features must have tests written before implementation
2. **100% coverage requirement** - All code must be covered by tests (milestone requirement, CI enforces 80% minimum for M0)
3. **Green CI required** - All tests must pass before merging
4. **No untested code** - Do not merge code without corresponding tests

## Development Workflow

### Branch Naming Convention

- Milestone branches: `tdd/m{N}-{description}` (e.g., `tdd/m1-data-context`)
- Feature branches: `feature/{milestone}-{feature-name}`
- Bug fixes: `fix/{milestone}-{bug-description}`

### Milestone Plan

See [TDD_PLAN.md](TDD_PLAN.md) for the complete milestone breakdown. Each milestone follows this structure:

- **M0** (Week 0): Repo & CI - Initialize layout, CI, coverage gates, test skeletons
- **M1** (Week 1-2): L1 Data/Context - Data ingestion, embeddings, leak-proof splits
- **M2** (Week 3-5): L2 Agents - Agent interfaces, futures/options, stocks, crypto, ETFs, contracts
- **M3** (Week 6-7): L3 Retraining - Meta-learner, local quantum mocks
- **M4** (Week 8-9): L4/L5 QAQC - Regression pack, robustness suite, performance SLOs
- **M5** (Week 10): L6 Strategy Optimization - Global objective, quantum-global mock
- **M6** (Week 11-12): L7 Execution - Adapters, pre-trade risk, kill-switch, telemetry
- **M7** (Week 13+): On-chain Alpha - Tokenization, vaults, DEX router
- **M8** (Future): RWA Alpha - Oracle attestation, compliant mint/burn

### CI Gates

All PRs must pass:
- **Linting**: flake8 with no errors
- **Tests**: All tests passing
- **Coverage**: Minimum 80% code coverage (100% for milestone completion)
- **Type checks**: (To be added in future milestones)
- **Security scans**: (To be added in future milestones)

### Making Changes

1. Create a branch following the naming convention
2. Write tests for your changes FIRST
3. Implement the feature to make tests pass
4. Run CI locally before pushing:
   ```bash
   # Install dependencies
   pip install -r requirements-dev.txt
   pip install -r requirements.txt
   
   # Run linter
   flake8 .
   
   # Run tests with coverage
   pytest --cov=. --cov-report=term-missing
   
   # Check coverage threshold
   coverage report --fail-under=80
   ```
5. Push and create a PR
6. Address review feedback
7. Merge only when CI is green and reviews approved

### Definition of Done

For each milestone:
- [ ] All referenced tests from TDD_PLAN.md are green
- [ ] Coverage is 100%
- [ ] Benchmarks hit (latency/throughput where applicable)
- [ ] Documentation updated
- [ ] Model cards updated (where applicable)
- [ ] Artifacts versioned
- [ ] Rollback tested

## Code Style

- Follow PEP 8
- Maximum line length: 127 characters
- Use meaningful variable names
- Add docstrings to all public functions/classes
- Keep functions focused and small

## Questions?

Refer to [TDD_PLAN.md](TDD_PLAN.md) for architecture and milestone details.
