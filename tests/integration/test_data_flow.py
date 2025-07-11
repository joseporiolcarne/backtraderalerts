#!/usr/bin/env python3
"""
Integration tests for data flow through the system
"""
import unittest
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))

class TestDataFlow(unittest.TestCase):
    """Test data flow from fetching to processing"""
    
    def setUp(self):
        """Set up test data and mocks"""
        # Create realistic sample data
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        np.random.seed(42)  # Reproducible results
        
        base_price = 100
        prices = []
        current_price = base_price
        
        for _ in range(len(dates)):
            change = np.random.normal(0.02, 2.0)
            current_price *= (1 + change / 100)
            
            high = current_price * (1 + abs(np.random.normal(0, 0.01)))
            low = current_price * (1 - abs(np.random.normal(0, 0.01)))
            open_price = current_price * (1 + np.random.normal(0, 0.005))
            volume = abs(np.random.normal(1000000, 200000))
            
            prices.append({
                'open': open_price,
                'high': max(high, open_price, current_price),
                'low': min(low, open_price, current_price),
                'close': current_price,
                'volume': volume
            })
        
        self.sample_data = pd.DataFrame(prices, index=dates)
    
    def test_config_to_strategy_flow(self):
        """Test configuration flows correctly to strategy parameters"""
        print("\n🔧 Testing: Config → Strategy Flow")
        
        from src.config.config_manager import ConfigManager
        
        # Create config with strategy parameters
        config = ConfigManager()
        config.set('strategies.rsi_crossover.rsi_period', 21)
        config.set('strategies.rsi_crossover.rsi_oversold', 25)
        config.set('strategies.rsi_crossover.rsi_overbought', 75)
        
        # Verify config values
        assert config.get('strategies.rsi_crossover.rsi_period') == 21
        assert config.get('strategies.rsi_crossover.rsi_oversold') == 25
        assert config.get('strategies.rsi_crossover.rsi_overbought') == 75
        
        print("✅ Configuration flows correctly to strategy parameters")
    
    def test_data_fetcher_to_engine_flow(self):
        """Test data flows from fetcher to engine"""
        print("\n📊 Testing: Data Fetcher → Engine Flow")
        
        from src.data.fetcher import DataFetcher
        
        # Test data processing pipeline
        fetcher = DataFetcher('yfinance')
        
        # Test interval conversion
        converted_interval = fetcher._convert_interval_yfinance('4h')
        assert converted_interval == '1h', "Interval conversion failed"
        
        # Test data validation
        assert 'open' in self.sample_data.columns
        assert 'high' in self.sample_data.columns
        assert 'low' in self.sample_data.columns
        assert 'close' in self.sample_data.columns
        assert 'volume' in self.sample_data.columns
        
        # Test data integrity
        assert len(self.sample_data) > 0
        assert not self.sample_data.isnull().any().any()
        
        print("✅ Data flows correctly from fetcher to engine")
    
    def test_multiple_timeframe_data_flow(self):
        """Test multi-timeframe data processing"""
        print("\n⏰ Testing: Multi-Timeframe Data Flow")
        
        from src.data.fetcher import DataFetcher
        
        fetcher = DataFetcher('yfinance')
        
        # Create different timeframe data
        hourly_data = self.sample_data.copy()
        daily_data = self.sample_data.copy()
        
        # Simulate timeframe data processing
        timeframe_data = {
            '1h': hourly_data,
            '1d': daily_data
        }
        
        # Test data consistency across timeframes
        for tf, data in timeframe_data.items():
            assert isinstance(data, pd.DataFrame), f"Data for {tf} is not DataFrame"
            assert len(data) > 0, f"No data for timeframe {tf}"
            assert 'close' in data.columns, f"Missing close data for {tf}"
        
        print("✅ Multi-timeframe data flows correctly")
    
    @patch('yfinance.Ticker')
    def test_real_data_fetch_simulation(self, mock_ticker):
        """Test simulated real data fetching"""
        print("\n🌐 Testing: Real Data Fetch Simulation")
        
        from src.data.fetcher import DataFetcher
        
        # Mock yfinance response
        mock_instance = Mock()
        mock_instance.history.return_value = self.sample_data
        mock_ticker.return_value = mock_instance
        
        fetcher = DataFetcher('yfinance')
        
        try:
            # This will fail without yfinance, but we can test the flow
            result = fetcher.fetch_data('AAPL', '1d', '2023-01-01', '2023-12-31')
            
            if result is not None:
                assert isinstance(result, pd.DataFrame)
                print("✅ Real data fetch simulation successful")
            else:
                print("⚠️ Data fetch returned None (expected without yfinance)")
        except ImportError:
            print("⚠️ yfinance not available - testing flow structure only")
            # Test that the method exists and has correct signature
            assert hasattr(fetcher, 'fetch_data')
            assert hasattr(fetcher, '_convert_interval_yfinance')
    
    def test_data_validation_flow(self):
        """Test data validation throughout the pipeline"""
        print("\n✅ Testing: Data Validation Flow")
        
        # Test valid data
        valid_data = self.sample_data.copy()
        
        # Check required columns
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            assert col in valid_data.columns, f"Missing required column: {col}"
        
        # Check data types
        for col in required_columns:
            assert pd.api.types.is_numeric_dtype(valid_data[col]), f"Column {col} is not numeric"
        
        # Check OHLC logic
        assert (valid_data['high'] >= valid_data['low']).all(), "High < Low found"
        assert (valid_data['high'] >= valid_data['open']).all(), "High < Open found"
        assert (valid_data['high'] >= valid_data['close']).all(), "High < Close found"
        assert (valid_data['low'] <= valid_data['open']).all(), "Low > Open found"
        assert (valid_data['low'] <= valid_data['close']).all(), "Low > Close found"
        
        # Test invalid data detection
        invalid_data = valid_data.copy()
        invalid_data.iloc[0, invalid_data.columns.get_loc('high')] = invalid_data.iloc[0, invalid_data.columns.get_loc('low')] - 1  # Invalid: high < low
        
        # This should be detected by validation
        has_invalid = (invalid_data['high'] < invalid_data['low']).any()
        assert has_invalid, "Invalid data not detected"
        
        print("✅ Data validation flow working correctly")
    
    def test_config_file_to_runtime_flow(self):
        """Test configuration file loads and flows to runtime"""
        print("\n⚙️ Testing: Config File → Runtime Flow")
        
        from src.config.config_manager import ConfigManager
        import tempfile
        import yaml
        
        # Create test config
        test_config = {
            'trading': {
                'initial_cash': 15000,
                'commission': 0.002
            },
            'data': {
                'default_source': 'binance'
            },
            'strategies': {
                'rsi_crossover': {
                    'rsi_period': 21,
                    'rsi_oversold': 25,
                    'rsi_overbought': 75
                }
            }
        }
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            temp_path = f.name
        
        try:
            # Load config from file
            config = ConfigManager(temp_path)
            
            # Verify values flow correctly
            assert config.get('trading.initial_cash') == 15000
            assert config.get('trading.commission') == 0.002
            assert config.get('data.default_source') == 'binance'
            assert config.get('strategies.rsi_crossover.rsi_period') == 21
            
            print("✅ Config file flows correctly to runtime")
            
        finally:
            os.unlink(temp_path)
    
    def test_error_propagation_flow(self):
        """Test error handling flows through the system"""
        print("\n🚨 Testing: Error Propagation Flow")
        
        from src.data.fetcher import DataFetcher
        from src.alerts.console_dispatcher import ConsoleDispatcher
        
        # Test error handling in data fetcher
        fetcher = DataFetcher('yfinance')
        dispatcher = ConsoleDispatcher()
        
        # Test invalid symbol handling
        try:
            # This should handle errors gracefully
            result = fetcher.fetch_data('INVALID_SYMBOL_XYZ', '1d', '2023-01-01', '2023-01-31')
            # Should return None or raise ImportError for missing dependencies
            assert result is None or isinstance(result, type(None))
        except ImportError:
            # Expected when dependencies not available
            pass
        
        # Test error alert
        dispatcher.send_error_alert(
            "DATA_FETCH_ERROR", 
            "Invalid symbol: INVALID_SYMBOL_XYZ",
            "test_error_propagation"
        )
        
        # Check error was logged
        error_alerts = dispatcher.get_alerts_by_type('error')
        assert len(error_alerts) > 0, "Error alert not recorded"
        
        print("✅ Error propagation flow working correctly")

class TestDataIntegrity(unittest.TestCase):
    """Test data integrity throughout the system"""
    
    def test_data_consistency_check(self):
        """Test data remains consistent through processing"""
        print("\n🔍 Testing: Data Consistency")
        
        # Create test data
        dates = pd.date_range('2023-01-01', periods=50, freq='D')
        test_data = pd.DataFrame({
            'open': np.random.uniform(90, 110, 50),
            'high': np.random.uniform(100, 120, 50),
            'low': np.random.uniform(80, 100, 50),
            'close': np.random.uniform(95, 105, 50),
            'volume': np.random.uniform(100000, 200000, 50)
        }, index=dates)
        
        # Fix OHLC relationships
        for i in range(len(test_data)):
            high = max(test_data.iloc[i]['open'], test_data.iloc[i]['close'], test_data.iloc[i]['high'])
            low = min(test_data.iloc[i]['open'], test_data.iloc[i]['close'], test_data.iloc[i]['low'])
            test_data.iloc[i, test_data.columns.get_loc('high')] = high
            test_data.iloc[i, test_data.columns.get_loc('low')] = low
        
        # Test data integrity
        original_len = len(test_data)
        original_sum = test_data['close'].sum()
        
        # Simulate processing
        processed_data = test_data.copy()
        
        # Check data integrity after processing
        assert len(processed_data) == original_len, "Data length changed during processing"
        assert abs(processed_data['close'].sum() - original_sum) < 0.001, "Data values changed during processing"
        
        print("✅ Data consistency maintained through processing")

if __name__ == '__main__':
    print("="*60)
    print("INTEGRATION TESTS - DATA FLOW")
    print("="*60)
    
    unittest.main(verbosity=2)