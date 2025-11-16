"""Configuration management for the AI trading engine."""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Configuration manager for the trading engine."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to configuration file. Defaults to config/default.json
        """
        self.config_path = config_path or os.path.join(
            Path(__file__).parent.parent.parent, 'config', 'default.json'
        )
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self._config = json.load(f)
        else:
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "data_ingestion": {
                "sources": ["yahoo_finance", "alpha_vantage"],
                "update_interval": 3600,
                "symbols": ["BTC-USD", "ETH-USD", "SPY"],
                "historical_period": "1y"
            },
            "market_agents": {
                "rl_enabled": True,
                "ml_models": ["lstm", "transformer", "gradient_boosting"],
                "training_interval": 86400,
                "exploration_rate": 0.1
            },
            "optimization": {
                "enabled": True,
                "algorithm": "reinforcement_learning",
                "risk_tolerance": 0.3,
                "max_position_size": 0.1
            },
            "encryption": {
                "algorithm": "kyber",
                "key_size": 3072,
                "enabled": True
            },
            "system": {
                "log_level": "INFO",
                "data_directory": "data",
                "model_directory": "models"
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'data_ingestion.sources')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Set configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self, path: Optional[str] = None):
        """
        Save configuration to file.
        
        Args:
            path: Path to save configuration. Defaults to loaded config path.
        """
        save_path = path or self.config_path
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    @property
    def all(self) -> Dict[str, Any]:
        """Get all configuration."""
        return self._config.copy()
