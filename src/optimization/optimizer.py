"""Real-time optimization for trading strategies."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from threading import Thread, Event, Lock
import time


class RealTimeOptimizer:
    """
    Real-time optimizer for trading strategies.
    
    Optimizes trade execution based on market predictions, risk management,
    and portfolio constraints using reinforcement learning.
    """
    
    def __init__(self, config, agent_manager):
        """
        Initialize real-time optimizer.
        
        Args:
            config: Configuration object
            agent_manager: Market agent manager instance
        """
        self.config = config
        self.agent_manager = agent_manager
        self.logger = logging.getLogger(__name__)
        
        self.enabled = config.get('optimization.enabled', True)
        self.algorithm = config.get('optimization.algorithm', 'reinforcement_learning')
        self.risk_tolerance = config.get('optimization.risk_tolerance', 0.3)
        self.max_position_size = config.get('optimization.max_position_size', 0.1)
        
        self._running = False
        self._thread: Optional[Thread] = None
        self._stop_event = Event()
        self._lock = Lock()
        
        # Portfolio state
        self._portfolio: Dict[str, Any] = {
            "cash": 100000.0,  # Starting capital
            "positions": {},
            "total_value": 100000.0,
            "trades": []
        }
        
        # Performance metrics
        self._metrics = {
            "total_trades": 0,
            "profitable_trades": 0,
            "total_profit": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0
        }
        
        self.logger.info(f"Initialized RealTimeOptimizer with algorithm: {self.algorithm}")
    
    def start(self):
        """Start the optimizer."""
        if self._running:
            self.logger.warning("Optimizer already running")
            return
        
        if not self.enabled:
            self.logger.info("Optimizer is disabled in configuration")
            return
        
        self._running = True
        self._stop_event.clear()
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()
        
        self.logger.info("Optimizer started")
    
    def stop(self):
        """Stop the optimizer."""
        if not self._running:
            return
        
        self._running = False
        self._stop_event.set()
        
        if self._thread:
            self._thread.join(timeout=5)
        
        self.logger.info("Optimizer stopped")
    
    def _run(self):
        """Main optimization loop."""
        while self._running and not self._stop_event.is_set():
            try:
                self._optimize_portfolio()
            except Exception as e:
                self.logger.error(f"Error in optimization: {e}")
            
            # Run optimization every 60 seconds
            self._stop_event.wait(60)
    
    def _optimize_portfolio(self):
        """Optimize portfolio based on current market conditions."""
        symbols = self.config.get('data_ingestion.symbols', [])
        
        for symbol in symbols:
            try:
                predictions = self.agent_manager.get_predictions(symbol)
                
                # Make trading decisions based on predictions
                decision = self._make_trading_decision(symbol, predictions)
                
                if decision['action'] != 'hold':
                    self._execute_internal_trade(symbol, decision)
            except Exception as e:
                self.logger.error(f"Error optimizing {symbol}: {e}")
    
    def _make_trading_decision(self, symbol: str, predictions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make trading decision based on predictions and risk management.
        
        Args:
            symbol: Trading symbol
            predictions: Predictions from market agents
            
        Returns:
            Trading decision
        """
        consensus = predictions.get('consensus', 'hold')
        confidence = predictions.get('confidence', 0.0)
        
        # Apply confidence threshold
        if confidence < 0.6:
            return {"action": "hold", "amount": 0.0, "reason": "low_confidence"}
        
        # Calculate position size based on risk tolerance
        with self._lock:
            max_trade_value = self._portfolio['total_value'] * self.max_position_size
        
        # Determine action and amount
        if consensus == 'buy':
            return {
                "action": "buy",
                "amount": max_trade_value * confidence,
                "confidence": confidence,
                "reason": "consensus_buy"
            }
        elif consensus == 'sell':
            # Check if we have position to sell
            with self._lock:
                if symbol in self._portfolio['positions']:
                    position_value = self._portfolio['positions'][symbol].get('value', 0)
                    return {
                        "action": "sell",
                        "amount": position_value * confidence,
                        "confidence": confidence,
                        "reason": "consensus_sell"
                    }
        
        return {"action": "hold", "amount": 0.0, "reason": "default"}
    
    def _execute_internal_trade(self, symbol: str, decision: Dict[str, Any]):
        """
        Execute trade internally (simulation).
        
        Args:
            symbol: Trading symbol
            decision: Trading decision
        """
        action = decision['action']
        amount = decision['amount']
        
        with self._lock:
            trade_record = {
                "timestamp": datetime.now().isoformat(),
                "symbol": symbol,
                "action": action,
                "amount": amount,
                "confidence": decision.get('confidence', 0.0),
                "reason": decision.get('reason', 'unknown')
            }
            
            self._portfolio['trades'].append(trade_record)
            self._metrics['total_trades'] += 1
            
            self.logger.info(f"Executed {action} for {symbol}: amount={amount:.2f}")
    
    def execute_trade(self, symbol: str, action: str, amount: float) -> Dict[str, Any]:
        """
        Execute a trade (external call).
        
        Args:
            symbol: Trading symbol
            action: Trade action ('buy' or 'sell')
            amount: Trade amount
            
        Returns:
            Trade execution result
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "Optimizer is disabled"
            }
        
        # Validate trade
        validation = self._validate_trade(symbol, action, amount)
        if not validation['valid']:
            return {
                "success": False,
                "error": validation['reason']
            }
        
        # Execute trade
        with self._lock:
            result = self._process_trade(symbol, action, amount)
        
        # Update agents with feedback
        self.agent_manager.update_agents(symbol, action, result)
        
        return result
    
    def _validate_trade(self, symbol: str, action: str, amount: float) -> Dict[str, Any]:
        """Validate trade parameters."""
        if action not in ['buy', 'sell']:
            return {"valid": False, "reason": "Invalid action"}
        
        if amount <= 0:
            return {"valid": False, "reason": "Invalid amount"}
        
        with self._lock:
            if action == 'buy' and amount > self._portfolio['cash']:
                return {"valid": False, "reason": "Insufficient cash"}
            
            if action == 'sell' and symbol not in self._portfolio['positions']:
                return {"valid": False, "reason": "No position to sell"}
        
        return {"valid": True, "reason": ""}
    
    def _process_trade(self, symbol: str, action: str, amount: float) -> Dict[str, Any]:
        """Process trade execution."""
        # Simulate trade execution
        # In production, this would integrate with actual trading APIs
        
        current_price = 100.0  # Placeholder
        
        if action == 'buy':
            shares = amount / current_price
            self._portfolio['cash'] -= amount
            
            if symbol not in self._portfolio['positions']:
                self._portfolio['positions'][symbol] = {
                    "shares": 0.0,
                    "avg_price": 0.0,
                    "value": 0.0
                }
            
            position = self._portfolio['positions'][symbol]
            total_shares = position['shares'] + shares
            position['avg_price'] = ((position['shares'] * position['avg_price']) + 
                                    (shares * current_price)) / total_shares
            position['shares'] = total_shares
            position['value'] = total_shares * current_price
        
        elif action == 'sell':
            position = self._portfolio['positions'][symbol]
            shares = min(amount / current_price, position['shares'])
            proceeds = shares * current_price
            
            self._portfolio['cash'] += proceeds
            position['shares'] -= shares
            position['value'] = position['shares'] * current_price
            
            profit = proceeds - (shares * position['avg_price'])
            self._metrics['total_profit'] += profit
            
            if profit > 0:
                self._metrics['profitable_trades'] += 1
            
            if position['shares'] <= 0:
                del self._portfolio['positions'][symbol]
        
        # Update total portfolio value
        self._portfolio['total_value'] = self._portfolio['cash']
        for pos in self._portfolio['positions'].values():
            self._portfolio['total_value'] += pos['value']
        
        return {
            "success": True,
            "symbol": symbol,
            "action": action,
            "amount": amount,
            "price": current_price,
            "timestamp": datetime.now().isoformat(),
            "profit": self._metrics['total_profit']
        }
    
    def get_portfolio(self) -> Dict[str, Any]:
        """Get current portfolio state."""
        with self._lock:
            return self._portfolio.copy()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        with self._lock:
            return self._metrics.copy()
    
    def get_status(self) -> Dict[str, Any]:
        """Get optimizer status."""
        return {
            "running": self._running,
            "enabled": self.enabled,
            "algorithm": self.algorithm,
            "risk_tolerance": self.risk_tolerance,
            "max_position_size": self.max_position_size,
            "portfolio_value": self._portfolio['total_value'],
            "metrics": self.get_metrics()
        }
