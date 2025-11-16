# API Documentation

## TradingEngine

Main orchestrator for the AI trading engine.

### Constructor

```python
TradingEngine(config: Optional[Config] = None)
```

Initialize the trading engine with optional configuration.

### Methods

#### `start()`
Start the trading engine and all subsystems.

```python
engine.start()
```

#### `stop()`
Stop the trading engine and all subsystems.

```python
engine.stop()
```

#### `get_status() -> Dict[str, Any]`
Get current status of the trading engine and all components.

```python
status = engine.get_status()
```

Returns:
```python
{
    "engine_status": "running" | "stopped",
    "timestamp": "ISO-8601 timestamp",
    "data_ingestion": {...},
    "market_agents": {...},
    "optimizer": {...},
    "encryption": {...}
}
```

#### `execute_trade(symbol: str, action: str, amount: float) -> Dict[str, Any]`
Execute a trade through the optimizer.

```python
result = engine.execute_trade("BTC-USD", "buy", 1000.0)
```

Parameters:
- `symbol`: Trading symbol (e.g., "BTC-USD")
- `action`: "buy" or "sell"
- `amount`: Trade amount in USD

Returns:
```python
{
    "success": True | False,
    "symbol": "BTC-USD",
    "action": "buy",
    "amount": 1000.0,
    "price": 42000.0,
    "timestamp": "ISO-8601 timestamp",
    "profit": 0.0
}
```

#### `get_predictions(symbol: str) -> Dict[str, Any]`
Get market predictions for a symbol from all agents.

```python
predictions = engine.get_predictions("BTC-USD")
```

Returns:
```python
{
    "symbol": "BTC-USD",
    "predictions": [
        {
            "action": "buy",
            "confidence": 0.75,
            "agent_id": "agent_lstm_0",
            "model_type": "lstm"
        },
        ...
    ],
    "consensus": "buy" | "sell" | "hold",
    "confidence": 0.75,
    "timestamp": "ISO-8601 timestamp"
}
```

## Config

Configuration manager for the trading engine.

### Constructor

```python
Config(config_path: Optional[str] = None)
```

Initialize configuration from file or use defaults.

### Methods

#### `get(key: str, default: Any = None) -> Any`
Get configuration value using dot notation.

```python
sources = config.get('data_ingestion.sources', [])
```

#### `set(key: str, value: Any)`
Set configuration value using dot notation.

```python
config.set('optimization.risk_tolerance', 0.5)
```

#### `save(path: Optional[str] = None)`
Save configuration to file.

```python
config.save('config/custom.json')
```

## DataIngestionManager

Manages historical and real-time data ingestion.

### Methods

#### `start()`
Start data ingestion background process.

#### `stop()`
Stop data ingestion.

#### `get_latest_data(symbol: str, source: Optional[str] = None) -> Optional[Dict]`
Get latest data for a symbol.

```python
data = data_manager.get_latest_data("BTC-USD")
```

#### `get_historical_data(symbol: str, period: Optional[str] = None) -> List[Dict]`
Get historical data for a symbol.

```python
historical = data_manager.get_historical_data("BTC-USD", "1y")
```

## MarketAgentManager

Manages RL/ML market agents.

### Methods

#### `start()`
Start agent manager and training cycles.

#### `stop()`
Stop agent manager.

#### `get_predictions(symbol: str) -> Dict[str, Any]`
Get predictions from all agents for a symbol.

#### `update_agents(symbol: str, action: str, result: Dict)`
Update agents with trade results (RL feedback).

```python
agent_manager.update_agents("BTC-USD", "buy", result)
```

## RealTimeOptimizer

Real-time trade optimizer with risk management.

### Methods

#### `start()`
Start optimizer background process.

#### `stop()`
Stop optimizer.

#### `execute_trade(symbol: str, action: str, amount: float) -> Dict`
Execute a trade with validation and risk checks.

#### `get_portfolio() -> Dict`
Get current portfolio state.

```python
portfolio = optimizer.get_portfolio()
```

Returns:
```python
{
    "cash": 100000.0,
    "positions": {
        "BTC-USD": {
            "shares": 2.5,
            "avg_price": 40000.0,
            "value": 105000.0
        }
    },
    "total_value": 205000.0,
    "trades": [...]
}
```

#### `get_metrics() -> Dict`
Get performance metrics.

```python
metrics = optimizer.get_metrics()
```

Returns:
```python
{
    "total_trades": 100,
    "profitable_trades": 65,
    "total_profit": 5000.0,
    "sharpe_ratio": 1.5,
    "max_drawdown": -0.15
}
```

## QuantumEncryption

Quantum-proof encryption layer.

### Methods

#### `encrypt(data: Union[str, bytes]) -> bytes`
Encrypt data using quantum-proof encryption.

```python
encrypted = encryption.encrypt("sensitive data")
```

#### `decrypt(encrypted_data: bytes) -> bytes`
Decrypt data.

```python
decrypted = encryption.decrypt(encrypted)
```

#### `sign(data: Union[str, bytes]) -> bytes`
Create quantum-proof digital signature.

```python
signature = encryption.sign("data to sign")
```

#### `verify(data: Union[str, bytes], signature: bytes) -> bool`
Verify digital signature.

```python
is_valid = encryption.verify("data to verify", signature)
```

#### `get_public_key() -> bytes`
Get public key for key exchange.

#### `get_status() -> dict`
Get encryption system status.
