import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigManager:
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            # Default to config.yaml in the config directory
            base_dir = Path(__file__).parent.parent.parent
            config_path = os.path.join(base_dir, 'config', 'config.yaml')
        
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            print(f"Config file not found at {self.config_path}. Using defaults.")
            return self.get_default_config()
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            'telegram': {
                'bot_token': '',
                'chat_id': ''
            },
            'trading': {
                'initial_cash': 10000,
                'commission': 0.001
            },
            'data': {
                'default_source': 'yfinance',
                'yfinance': {},
                'binance': {
                    'api_key': '',
                    'api_secret': ''
                }
            },
            'strategies': {
                'rsi_crossover': {
                    'rsi_period': 14,
                    'rsi_oversold': 30,
                    'rsi_overbought': 70
                }
            },
            'backtest': {
                'default_symbol': 'BTC-USD',
                'default_interval': '1d',
                'default_lookback_days': 365
            },
            'live_trading': {
                'enabled': False,
                'update_interval': 60,
                'max_position_size': 1.0
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/backtrader_alerts.log',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        }
    
    def save_config(self, config: Optional[Dict[str, Any]] = None):
        """Save configuration to YAML file"""
        if config is None:
            config = self.config
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        with open(self.config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        Example: config.get('telegram.bot_token')
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        """
        Set configuration value using dot notation
        Example: config.set('telegram.bot_token', 'your_token')
        """
        keys = key_path.split('.')
        
        # Ensure self.config is initialized
        if self.config is None:
            self.config = {}
        
        config = self.config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if config is None:
                config = {}
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
    
    def update_from_dict(self, updates: Dict[str, Any]):
        """Update configuration from a dictionary"""
        def deep_update(d, u):
            for k, v in u.items():
                if isinstance(v, dict):
                    d[k] = deep_update(d.get(k, {}), v)
                else:
                    d[k] = v
            return d
        
        self.config = deep_update(self.config, updates)
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        # Check required fields for Telegram if enabled
        if self.get('telegram.bot_token') and not self.get('telegram.chat_id'):
            print("Warning: Telegram bot token provided but chat ID is missing")
            return False
        
        # Check trading parameters
        if self.get('trading.initial_cash', 0) <= 0:
            print("Error: Initial cash must be positive")
            return False
        
        if not 0 <= self.get('trading.commission', 0) <= 1:
            print("Error: Commission must be between 0 and 1")
            return False
        
        return True
    
    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access"""
        return self.get(key)
    
    def __setitem__(self, key: str, value: Any):
        """Allow dictionary-style setting"""
        self.set(key, value)