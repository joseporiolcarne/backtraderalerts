import unittest
import tempfile
import os
import yaml
from unittest.mock import patch, mock_open
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.config_manager import ConfigManager
from src.config.indicators_config import (
    INDICATOR_CONFIGS, get_indicator_by_category, 
    get_indicator_categories, get_indicator_params, get_indicator_lines
)

class TestConfigManager(unittest.TestCase):
    
    def setUp(self):
        self.test_config = {
            'telegram': {
                'bot_token': 'test_token',
                'chat_id': 'test_chat_id'
            },
            'trading': {
                'initial_cash': 10000,
                'commission': 0.001
            },
            'data': {
                'default_source': 'yfinance'
            }
        }
    
    def test_init_with_valid_config_file(self):
        """Test initialization with a valid config file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(self.test_config, f)
            temp_path = f.name
        
        try:
            config_manager = ConfigManager(temp_path)
            self.assertEqual(config_manager.config['telegram']['bot_token'], 'test_token')
            self.assertEqual(config_manager.config['trading']['initial_cash'], 10000)
        finally:
            os.unlink(temp_path)
    
    def test_init_with_nonexistent_file(self):
        """Test initialization with non-existent config file"""
        config_manager = ConfigManager('/nonexistent/path/config.yaml')
        
        # Should load default config
        default_config = config_manager.get_default_config()
        self.assertEqual(config_manager.config, default_config)
    
    def test_init_without_config_path(self):
        """Test initialization without specifying config path"""
        # This will try to load from default location, which likely doesn't exist
        config_manager = ConfigManager()
        
        # Should load default config
        self.assertIsInstance(config_manager.config, dict)
        self.assertIn('telegram', config_manager.config)
        self.assertIn('trading', config_manager.config)
    
    @patch('builtins.open', new_callable=mock_open, read_data="invalid: yaml: content:")
    def test_init_with_invalid_yaml(self, mock_file):
        """Test initialization with invalid YAML"""
        config_manager = ConfigManager('invalid.yaml')
        
        # Should load default config
        default_config = config_manager.get_default_config()
        self.assertEqual(config_manager.config, default_config)
    
    def test_get_default_config(self):
        """Test default configuration structure"""
        config_manager = ConfigManager()
        default_config = config_manager.get_default_config()
        
        self.assertIsInstance(default_config, dict)
        self.assertIn('telegram', default_config)
        self.assertIn('trading', default_config)
        self.assertIn('data', default_config)
        self.assertIn('strategies', default_config)
        self.assertIn('backtest', default_config)
        self.assertIn('live_trading', default_config)
        self.assertIn('logging', default_config)
        
        # Check default values
        self.assertEqual(default_config['trading']['initial_cash'], 10000)
        self.assertEqual(default_config['trading']['commission'], 0.001)
        self.assertEqual(default_config['data']['default_source'], 'yfinance')
    
    def test_get_simple_key(self):
        """Test getting simple configuration values"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(self.test_config, f)
            temp_path = f.name
        
        try:
            config_manager = ConfigManager(temp_path)
            
            # Test getting nested values with dot notation
            self.assertEqual(config_manager.get('telegram.bot_token'), 'test_token')
            self.assertEqual(config_manager.get('trading.initial_cash'), 10000)
            self.assertEqual(config_manager.get('data.default_source'), 'yfinance')
        finally:
            os.unlink(temp_path)
    
    def test_get_nonexistent_key(self):
        """Test getting non-existent configuration key"""
        config_manager = ConfigManager()
        
        # Should return default value
        self.assertIsNone(config_manager.get('nonexistent.key'))
        self.assertEqual(config_manager.get('nonexistent.key', 'default'), 'default')
    
    def test_set_simple_key(self):
        """Test setting configuration values"""
        config_manager = ConfigManager()
        
        config_manager.set('telegram.bot_token', 'new_token')
        self.assertEqual(config_manager.get('telegram.bot_token'), 'new_token')
        
        config_manager.set('trading.initial_cash', 20000)
        self.assertEqual(config_manager.get('trading.initial_cash'), 20000)
    
    def test_set_new_nested_key(self):
        """Test setting new nested configuration key"""
        config_manager = ConfigManager()
        
        config_manager.set('new.nested.key', 'value')
        self.assertEqual(config_manager.get('new.nested.key'), 'value')
    
    def test_update_from_dict(self):
        """Test updating configuration from dictionary"""
        config_manager = ConfigManager()
        
        updates = {
            'telegram': {
                'bot_token': 'updated_token'
            },
            'trading': {
                'initial_cash': 15000
            },
            'new_section': {
                'new_key': 'new_value'
            }
        }
        
        config_manager.update_from_dict(updates)
        
        self.assertEqual(config_manager.get('telegram.bot_token'), 'updated_token')
        self.assertEqual(config_manager.get('trading.initial_cash'), 15000)
        self.assertEqual(config_manager.get('new_section.new_key'), 'new_value')
    
    def test_validate_config_valid(self):
        """Test configuration validation with valid config"""
        config_manager = ConfigManager()
        config_manager.set('telegram.bot_token', 'valid_token')
        config_manager.set('telegram.chat_id', 'valid_chat_id')
        config_manager.set('trading.initial_cash', 10000)
        config_manager.set('trading.commission', 0.001)
        
        self.assertTrue(config_manager.validate_config())
    
    def test_validate_config_missing_chat_id(self):
        """Test configuration validation with missing chat ID"""
        config_manager = ConfigManager()
        config_manager.set('telegram.bot_token', 'valid_token')
        config_manager.set('telegram.chat_id', '')  # Empty chat ID
        
        self.assertFalse(config_manager.validate_config())
    
    def test_validate_config_invalid_cash(self):
        """Test configuration validation with invalid initial cash"""
        config_manager = ConfigManager()
        config_manager.set('trading.initial_cash', 0)  # Invalid: should be positive
        
        self.assertFalse(config_manager.validate_config())
    
    def test_validate_config_invalid_commission(self):
        """Test configuration validation with invalid commission"""
        config_manager = ConfigManager()
        config_manager.set('trading.commission', 1.5)  # Invalid: should be between 0 and 1
        
        self.assertFalse(config_manager.validate_config())
    
    def test_dictionary_style_access(self):
        """Test dictionary-style access to configuration"""
        config_manager = ConfigManager()
        
        # Test getitem
        value = config_manager['trading.initial_cash']
        self.assertEqual(value, config_manager.get('trading.initial_cash'))
        
        # Test setitem
        config_manager['trading.initial_cash'] = 25000
        self.assertEqual(config_manager.get('trading.initial_cash'), 25000)
    
    def test_save_config(self):
        """Test saving configuration to file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = f.name
        
        try:
            config_manager = ConfigManager(temp_path)
            config_manager.set('test.key', 'test_value')
            
            # Save configuration
            config_manager.save_config()
            
            # Load and verify
            new_config_manager = ConfigManager(temp_path)
            self.assertEqual(new_config_manager.get('test.key'), 'test_value')
        finally:
            os.unlink(temp_path)
    
    def test_save_specific_config(self):
        """Test saving specific configuration dictionary"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = f.name
        
        try:
            config_manager = ConfigManager(temp_path)
            
            custom_config = {'custom': {'key': 'value'}}
            config_manager.save_config(custom_config)
            
            # Load and verify
            new_config_manager = ConfigManager(temp_path)
            self.assertEqual(new_config_manager.get('custom.key'), 'value')
        finally:
            os.unlink(temp_path)

class TestIndicatorsConfig(unittest.TestCase):
    
    def test_indicator_configs_structure(self):
        """Test that INDICATOR_CONFIGS has the expected structure"""
        self.assertIsInstance(INDICATOR_CONFIGS, dict)
        self.assertGreater(len(INDICATOR_CONFIGS), 0)
        
        # Check that each indicator has required fields
        for ind_name, ind_config in INDICATOR_CONFIGS.items():
            self.assertIsInstance(ind_name, str)
            self.assertIsInstance(ind_config, dict)
            
            self.assertIn('class', ind_config)
            self.assertIn('description', ind_config)
            self.assertIn('params', ind_config)
            self.assertIn('lines', ind_config)
            self.assertIn('category', ind_config)
            
            self.assertIsInstance(ind_config['class'], str)
            self.assertIsInstance(ind_config['description'], str)
            self.assertIsInstance(ind_config['params'], dict)
            self.assertIsInstance(ind_config['lines'], list)
            self.assertIsInstance(ind_config['category'], str)
    
    def test_specific_indicators_exist(self):
        """Test that specific indicators are defined"""
        expected_indicators = ['RSI', 'SMA', 'EMA', 'BollingerBands', 'MACD', 'CCI']
        
        for indicator in expected_indicators:
            self.assertIn(indicator, INDICATOR_CONFIGS)
    
    def test_get_indicator_by_category(self):
        """Test getting indicators by category"""
        momentum_indicators = get_indicator_by_category('momentum')
        self.assertIsInstance(momentum_indicators, dict)
        
        # RSI should be in momentum category
        self.assertIn('RSI', momentum_indicators)
        
        # Check that all returned indicators are indeed momentum indicators
        for ind_name, ind_config in momentum_indicators.items():
            self.assertEqual(ind_config['category'], 'momentum')
    
    def test_get_indicator_by_invalid_category(self):
        """Test getting indicators by invalid category"""
        result = get_indicator_by_category('invalid_category')
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 0)
    
    def test_get_indicator_categories(self):
        """Test getting all indicator categories"""
        categories = get_indicator_categories()
        self.assertIsInstance(categories, list)
        self.assertGreater(len(categories), 0)
        
        expected_categories = ['momentum', 'trend', 'volatility', 'volume']
        for category in expected_categories:
            self.assertIn(category, categories)
    
    def test_get_indicator_params(self):
        """Test getting indicator parameters"""
        # Test RSI parameters
        rsi_params = get_indicator_params('RSI')
        self.assertIsInstance(rsi_params, dict)
        self.assertIn('period', rsi_params)
        
        # Test SMA parameters
        sma_params = get_indicator_params('SMA')
        self.assertIsInstance(sma_params, dict)
        self.assertIn('period', sma_params)
        
        # Test invalid indicator
        invalid_params = get_indicator_params('INVALID_INDICATOR')
        self.assertIsInstance(invalid_params, dict)
        self.assertEqual(len(invalid_params), 0)
    
    def test_get_indicator_lines(self):
        """Test getting indicator line names"""
        # Test RSI lines
        rsi_lines = get_indicator_lines('RSI')
        self.assertIsInstance(rsi_lines, list)
        self.assertIn('rsi', rsi_lines)
        
        # Test Bollinger Bands lines
        bb_lines = get_indicator_lines('BollingerBands')
        self.assertIsInstance(bb_lines, list)
        self.assertIn('mid', bb_lines)
        self.assertIn('top', bb_lines)
        self.assertIn('bot', bb_lines)
        
        # Test invalid indicator
        invalid_lines = get_indicator_lines('INVALID_INDICATOR')
        self.assertIsInstance(invalid_lines, list)
        self.assertEqual(len(invalid_lines), 0)
    
    def test_indicator_param_types(self):
        """Test that indicator parameters have correct type information"""
        for ind_name, ind_config in INDICATOR_CONFIGS.items():
            params = ind_config['params']
            
            for param_name, param_config in params.items():
                self.assertIsInstance(param_config, dict)
                self.assertIn('default', param_config)
                self.assertIn('type', param_config)
                
                # Check type consistency
                param_type = param_config['type']
                param_default = param_config['default']
                
                if param_type == 'int':
                    self.assertIsInstance(param_default, int)
                elif param_type == 'float':
                    self.assertIsInstance(param_default, float)
    
    def test_indicator_ranges(self):
        """Test indicator ranges are properly defined"""
        for ind_name, ind_config in INDICATOR_CONFIGS.items():
            range_val = ind_config.get('range')
            
            if range_val is not None:
                self.assertIsInstance(range_val, tuple)
                self.assertEqual(len(range_val), 2)
                self.assertIsInstance(range_val[0], (int, float))
                self.assertIsInstance(range_val[1], (int, float))
                self.assertLess(range_val[0], range_val[1])

if __name__ == '__main__':
    unittest.main()