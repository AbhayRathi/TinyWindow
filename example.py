#!/usr/bin/env python3
"""
Example usage of TinyWindow AI Trading Engine
"""

import time
from src.core import TradingEngine, Config


def main():
    """Demonstrate basic usage of the trading engine."""
    
    print("=" * 60)
    print("TinyWindow AI Trading Engine - Example Usage")
    print("=" * 60)
    
    # 1. Initialize the engine
    print("\n1. Initializing trading engine...")
    engine = TradingEngine()
    
    # 2. Check status before starting
    print("\n2. Checking initial status...")
    status = engine.get_status()
    print(f"   Engine Status: {status['engine_status']}")
    print(f"   Portfolio Value: ${status['optimizer']['portfolio_value']:,.2f}")
    
    # 3. Start the engine
    print("\n3. Starting the engine...")
    engine.start()
    
    # Wait a moment for components to initialize
    time.sleep(2)
    
    # 4. Get predictions for a symbol
    print("\n4. Getting market predictions...")
    predictions = engine.get_predictions("BTC-USD")
    print(f"   Symbol: {predictions['symbol']}")
    print(f"   Consensus: {predictions['consensus']}")
    print(f"   Confidence: {predictions['confidence']:.2%}")
    print(f"   Number of agents: {len(predictions['predictions'])}")
    
    # 5. Execute a trade
    print("\n5. Executing a test trade...")
    try:
        result = engine.execute_trade("BTC-USD", "buy", 1000.0)
        if result['success']:
            print(f"   ✓ Trade executed successfully")
            print(f"   Symbol: {result['symbol']}")
            print(f"   Action: {result['action']}")
            print(f"   Amount: ${result['amount']:,.2f}")
        else:
            print(f"   ✗ Trade failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   ✗ Trade error: {e}")
    
    # 6. Get portfolio status
    print("\n6. Checking portfolio...")
    portfolio = engine.optimizer.get_portfolio()
    print(f"   Cash: ${portfolio['cash']:,.2f}")
    print(f"   Total Value: ${portfolio['total_value']:,.2f}")
    print(f"   Positions: {len(portfolio['positions'])}")
    
    # 7. Get performance metrics
    print("\n7. Performance metrics...")
    metrics = engine.optimizer.get_metrics()
    print(f"   Total Trades: {metrics['total_trades']}")
    print(f"   Profitable Trades: {metrics['profitable_trades']}")
    print(f"   Total Profit: ${metrics['total_profit']:,.2f}")
    
    # 8. Demonstrate encryption
    print("\n8. Testing quantum-proof encryption...")
    test_data = "Sensitive trading data"
    encrypted = engine.encryption.encrypt(test_data)
    decrypted = engine.encryption.decrypt(encrypted).decode('utf-8')
    print(f"   Original: {test_data}")
    print(f"   Encrypted: {encrypted[:50]}... ({len(encrypted)} bytes)")
    print(f"   Decrypted: {decrypted}")
    print(f"   Match: {test_data == decrypted}")
    
    # 9. Check final status
    print("\n9. Final status check...")
    final_status = engine.get_status()
    print(f"   Data Ingestion Running: {final_status['data_ingestion']['running']}")
    print(f"   Market Agents Running: {final_status['market_agents']['running']}")
    print(f"   Optimizer Running: {final_status['optimizer']['running']}")
    
    # 10. Stop the engine
    print("\n10. Stopping the engine...")
    engine.stop()
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    main()
