# TinyWindow Trading Engine - Source Code

## Architecture

**Core Engine** (`src/core/`)
- `TradingEngine`: Orchestrates all subsystems with unified lifecycle management
- `Config`: JSON-based hierarchical configuration with dot-notation access and runtime updates

**Data Ingestion** (`src/data_ingestion/`)
- Multi-source aggregation with pluggable providers (Yahoo Finance, Alpha Vantage)
- Background thread for periodic updates (configurable interval)
- Encrypted persistence and in-memory caching

**Market Agents** (`src/market_agents/`)
- Three agent types: LSTM, Transformer, Gradient Boosting
- RL-enabled continuous learning with feedback loops
- Confidence-weighted consensus mechanism for robust predictions
- Periodic retraining on new data

**Real-time Optimizer** (`src/optimization/`)
- RL-based trade decision making
- Risk management: position sizing, tolerance thresholds
- Portfolio tracking with performance metrics (Sharpe ratio, drawdown)

**Quantum Encryption** (`src/encryption/`)
- Kyber lattice-based encryption (3072-bit keys)
- NIST post-quantum cryptography standards
- Digital signatures for data integrity

## Usage

```python
from src.core import TradingEngine

engine = TradingEngine()
engine.start()

# Multi-agent consensus predictions
predictions = engine.get_predictions("BTC-USD")
# Returns: {consensus: "buy", confidence: 0.75, predictions: [...]}

# Risk-managed trade execution
result = engine.execute_trade("BTC-USD", "buy", 1000.0)

engine.stop()
```

## Threading Model

- Main: Application lifecycle
- Data ingestion: Periodic fetch + cache updates
- Agent manager: Periodic training cycles
- Optimizer: Continuous portfolio optimization

Lock-based synchronization for shared state, event-based coordination for threads.

## Configuration

```json
{
  "data_ingestion": {"sources": ["..."], "update_interval": 3600},
  "market_agents": {"ml_models": ["lstm", "transformer", "gradient_boosting"], "rl_enabled": true},
  "optimization": {"risk_tolerance": 0.3, "max_position_size": 0.1},
  "encryption": {"algorithm": "kyber", "key_size": 3072}
}
```

## Notes

Current implementation uses placeholder algorithms for ML models and data APIs. Production deployment requires:
- Real market data API integration
- Actual neural network implementations (TensorFlow/PyTorch)
- Production-grade post-quantum crypto libraries (liboqs)
- Persistent database backend
