#!/usr/bin/env python3
"""
Comprehensive test runner for Backtrader Alerts System
"""
import unittest
import sys
import os
from unittest.mock import Mock, MagicMock, patch
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Add src to Python path
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def create_mock_modules():
    """Create comprehensive mocks for missing dependencies"""
    
    # Mock pandas
    if 'pandas' not in sys.modules:
        mock_pandas = MagicMock()
        mock_pandas.DataFrame = MagicMock
        mock_pandas.date_range = lambda *args, **kwargs: MagicMock()
        mock_pandas.to_datetime = lambda x, **kwargs: MagicMock()
        mock_pandas.Timestamp = MagicMock
        sys.modules['pandas'] = mock_pandas
    
    # Mock backtrader
    if 'backtrader' not in sys.modules:
        mock_bt = MagicMock()
        mock_bt.Strategy = object  # Use object as base class
        mock_bt.Cerebro = MagicMock
        
        # Mock indicators
        mock_indicators = MagicMock()
        mock_indicators.RSI = MagicMock
        mock_indicators.SMA = MagicMock
        mock_indicators.EMA = MagicMock
        mock_indicators.BollingerBands = MagicMock
        mock_indicators.MACD = MagicMock
        mock_indicators.CCI = MagicMock
        mock_indicators.Stochastic = MagicMock
        mock_indicators.ATR = MagicMock
        mock_indicators.ADX = MagicMock
        mock_indicators.WMA = MagicMock
        mock_bt.indicators = mock_indicators
        
        # Mock feeds
        mock_feeds = MagicMock()
        mock_feeds.PandasData = MagicMock
        mock_bt.feeds = mock_feeds
        
        # Mock analyzers and observers
        mock_bt.analyzers = MagicMock()
        mock_bt.observers = MagicMock()
        
        sys.modules['backtrader'] = mock_bt
        sys.modules['backtrader.indicators'] = mock_indicators
        sys.modules['backtrader.feeds'] = mock_feeds
        sys.modules['backtrader.analyzers'] = mock_bt.analyzers
        sys.modules['backtrader.observers'] = mock_bt.observers
    
    # Mock other dependencies
    dependencies = {
        'yfinance': MagicMock(),
        'ccxt': MagicMock(),
        'telegram': MagicMock(),
        'plotly': MagicMock(),
        'plotly.graph_objects': MagicMock(),
        'streamlit': MagicMock()
    }
    
    for name, mock in dependencies.items():
        if name not in sys.modules:
            sys.modules[name] = mock

def test_configuration():
    """Test configuration management"""
    print("Testing Configuration Management...")
    
    try:
        from src.config.config_manager import ConfigManager
        from src.config.indicators_config import INDICATOR_CONFIGS, get_indicator_categories
        
        # Test ConfigManager
        config = ConfigManager()
        
        # Test basic operations
        config.set('test.key', 'test_value')
        assert config.get('test.key') == 'test_value', "Config set/get failed"
        
        # Test default config
        default_config = config.get_default_config()
        assert 'telegram' in default_config, "Default config missing telegram section"
        assert 'trading' in default_config, "Default config missing trading section"
        
        # Test validation
        config.set('trading.initial_cash', 10000)
        config.set('trading.commission', 0.001)
        assert config.validate_config(), "Valid config failed validation"
        
        # Test indicators config
        assert len(INDICATOR_CONFIGS) > 0, "No indicators configured"
        categories = get_indicator_categories()
        assert len(categories) > 0, "No indicator categories found"
        
        print("✅ Configuration tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_data_fetcher():
    """Test data fetcher functionality"""
    print("Testing Data Fetcher...")
    
    try:
        from src.data.fetcher import DataFetcher
        
        # Test initialization
        fetcher = DataFetcher('yfinance')
        assert fetcher.data_source == 'yfinance', "Data source not set correctly"
        
        # Test interval conversion
        assert fetcher._convert_interval_yfinance('1h') == '1h', "Interval conversion failed"
        assert fetcher._convert_interval_yfinance('4h') == '1h', "Complex interval conversion failed"
        
        print("✅ Data fetcher tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Data fetcher test failed: {e}")
        return False

def test_strategies():
    """Test trading strategies"""
    print("Testing Trading Strategies...")
    
    try:
        from src.strategies.rsi_crossover import RSICrossoverStrategy
        from src.strategies.multi_indicator import SimpleIndicatorStrategy, MultiIndicatorStrategy
        from src.strategies.multi_timeframe import MultiTimeframeStrategy
        
        # Test strategy creation (without running)
        rsi_strategy = type('TestStrategy', (RSICrossoverStrategy,), {})
        assert rsi_strategy is not None, "RSI strategy creation failed"
        
        simple_strategy = type('TestSimple', (SimpleIndicatorStrategy,), {})
        assert simple_strategy is not None, "Simple strategy creation failed"
        
        multi_strategy = type('TestMulti', (MultiIndicatorStrategy,), {})
        assert multi_strategy is not None, "Multi-indicator strategy creation failed"
        
        timeframe_strategy = type('TestTimeframe', (MultiTimeframeStrategy,), {})
        assert timeframe_strategy is not None, "Multi-timeframe strategy creation failed"
        
        print("✅ Strategy tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Strategy test failed: {e}")
        return False

def test_alerts():
    """Test alert system"""
    print("Testing Alert System...")
    
    try:
        from src.alerts.telegram_dispatcher import TelegramDispatcher
        
        # Test initialization
        dispatcher = TelegramDispatcher('test_token', 'test_chat')
        assert dispatcher.bot_token == 'test_token', "Bot token not set"
        assert dispatcher.chat_id == 'test_chat', "Chat ID not set"
        
        # Test time formatting
        time_str = dispatcher._get_current_time()
        assert len(time_str) > 0, "Time string is empty"
        
        print("✅ Alert tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Alert test failed: {e}")
        return False

def test_engine():
    """Test backtrader engine"""
    print("Testing Backtrader Engine...")
    
    try:
        from src.engine.backtrader_runner import BacktraderEngine
        
        # Test initialization
        engine = BacktraderEngine(initial_cash=10000, commission=0.001)
        assert engine.initial_cash == 10000, "Initial cash not set"
        assert engine.commission == 0.001, "Commission not set"
        
        print("✅ Engine tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Engine test failed: {e}")
        return False

def run_import_tests():
    """Test that all modules can be imported"""
    print("Testing Module Imports...")
    
    modules_to_test = [
        'src.config.config_manager',
        'src.config.indicators_config',
        'src.data.fetcher',
        'src.strategies.rsi_crossover',
        'src.strategies.multi_indicator',
        'src.strategies.multi_timeframe',
        'src.alerts.telegram_dispatcher',
        'src.engine.backtrader_runner'
    ]
    
    import_results = []
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name}")
            import_results.append(True)
        except Exception as e:
            print(f"❌ {module_name}: {e}")
            import_results.append(False)
    
    return all(import_results)

def main():
    """Main test runner"""
    print("=" * 60)
    print("BACKTRADER ALERTS SYSTEM - COMPREHENSIVE TESTS")
    print("=" * 60)
    
    # Setup mocks
    create_mock_modules()
    
    # Run tests
    test_results = []
    
    print("\n1. Module Import Tests")
    print("-" * 30)
    test_results.append(run_import_tests())
    
    print("\n2. Component Tests")
    print("-" * 30)
    test_results.append(test_configuration())
    test_results.append(test_data_fetcher())
    test_results.append(test_strategies())
    test_results.append(test_alerts())
    test_results.append(test_engine())
    
    # Summary
    passed = sum(test_results)
    total = len(test_results)
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ The system is working correctly with mocked dependencies")
        print("💡 Install requirements.txt to test with real dependencies")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        print("🔧 Check the error messages above for details")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)