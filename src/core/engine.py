"""Main Trading Engine orchestrator."""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from .config import Config
from ..data_ingestion.ingestion import DataIngestionManager
from ..market_agents.agent_manager import MarketAgentManager
from ..optimization.optimizer import RealTimeOptimizer
from ..encryption.quantum_encryption import QuantumEncryption


class TradingEngine:
    """
    Main orchestrator for the AI trading engine.
    
    Coordinates all components: data ingestion, market agents, optimization,
    and encryption to create a self-learning, self-securing trading ecosystem.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the trading engine.
        
        Args:
            config: Configuration object. If None, uses default configuration.
        """
        self.config = config or Config()
        self._setup_logging()
        
        # Initialize components
        self.logger.info("Initializing TinyWindow AI Trading Engine...")
        
        self.encryption = QuantumEncryption(
            algorithm=self.config.get('encryption.algorithm'),
            key_size=self.config.get('encryption.key_size')
        )
        
        self.data_manager = DataIngestionManager(
            config=self.config,
            encryption=self.encryption
        )
        
        self.agent_manager = MarketAgentManager(
            config=self.config,
            data_manager=self.data_manager
        )
        
        self.optimizer = RealTimeOptimizer(
            config=self.config,
            agent_manager=self.agent_manager
        )
        
        self.is_running = False
        self.logger.info("Trading engine initialized successfully")
    
    def _setup_logging(self):
        """Set up logging configuration."""
        log_level = self.config.get('system.log_level', 'INFO')
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def start(self):
        """Start the trading engine."""
        if self.is_running:
            self.logger.warning("Trading engine is already running")
            return
        
        self.logger.info("Starting trading engine...")
        self.is_running = True
        
        # Start data ingestion
        self.data_manager.start()
        
        # Start market agents
        self.agent_manager.start()
        
        # Start optimizer
        self.optimizer.start()
        
        self.logger.info("Trading engine started successfully")
    
    def stop(self):
        """Stop the trading engine."""
        if not self.is_running:
            self.logger.warning("Trading engine is not running")
            return
        
        self.logger.info("Stopping trading engine...")
        self.is_running = False
        
        # Stop components in reverse order
        self.optimizer.stop()
        self.agent_manager.stop()
        self.data_manager.stop()
        
        self.logger.info("Trading engine stopped successfully")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the trading engine.
        
        Returns:
            Dictionary containing status of all components
        """
        return {
            "engine_status": "running" if self.is_running else "stopped",
            "timestamp": datetime.now().isoformat(),
            "data_ingestion": self.data_manager.get_status(),
            "market_agents": self.agent_manager.get_status(),
            "optimizer": self.optimizer.get_status(),
            "encryption": self.encryption.get_status()
        }
    
    def execute_trade(self, symbol: str, action: str, amount: float) -> Dict[str, Any]:
        """
        Execute a trade through the optimizer.
        
        Args:
            symbol: Trading symbol
            action: Trade action ('buy' or 'sell')
            amount: Trade amount
            
        Returns:
            Trade execution result
        """
        if not self.is_running:
            raise RuntimeError("Trading engine is not running")
        
        return self.optimizer.execute_trade(symbol, action, amount)
    
    def get_predictions(self, symbol: str) -> Dict[str, Any]:
        """
        Get market predictions for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Predictions from market agents
        """
        return self.agent_manager.get_predictions(symbol)
