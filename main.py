#!/usr/bin/env python3
"""
TinyWindow AI Trading Engine
Main entry point for the trading system.
"""

import sys
import signal
import argparse
from src.core import TradingEngine, Config


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print("\nShutting down TinyWindow AI Trading Engine...")
    sys.exit(0)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='TinyWindow: Multi-layer AI Trading Engine'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file',
        default=None
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Print system status and exit'
    )
    
    args = parser.parse_args()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize configuration
    config = Config(args.config)
    
    # Initialize trading engine
    engine = TradingEngine(config)
    
    if args.status:
        # Print status and exit
        status = engine.get_status()
        print("\n=== TinyWindow AI Trading Engine Status ===")
        print(f"Engine Status: {status['engine_status']}")
        print(f"Timestamp: {status['timestamp']}")
        print(f"\nData Ingestion: {status['data_ingestion']}")
        print(f"Market Agents: {status['market_agents']}")
        print(f"Optimizer: {status['optimizer']}")
        print(f"Encryption: {status['encryption']}")
        return
    
    # Start the engine
    print("Starting TinyWindow AI Trading Engine...")
    print("=" * 60)
    print("Multi-layer AI Trading Engine for Decentralized Finance")
    print("Features:")
    print("  - Historical Data Ingestion")
    print("  - RL/ML Market Agents")
    print("  - Real-time Optimization")
    print("  - Quantum-proof Encryption")
    print("=" * 60)
    
    engine.start()
    
    print("\nEngine started. Press Ctrl+C to stop.")
    
    # Keep the main thread alive
    try:
        signal.pause()
    except AttributeError:
        # signal.pause() not available on Windows
        import time
        while True:
            time.sleep(1)


if __name__ == '__main__':
    main()
