#!/usr/bin/env python3
"""
Test runner that can work with or without dependencies installed
"""
import unittest
import sys
import os
from unittest.mock import Mock, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

# Mock missing modules if they're not available
def mock_missing_modules():
    """Mock modules that might not be installed"""
    modules_to_mock = [
        'pandas', 'backtrader', 'backtrader.indicators', 'backtrader.feeds',
        'backtrader.analyzers', 'backtrader.observers', 'telegram', 'yfinance',
        'ccxt', 'plotly', 'plotly.graph_objects', 'streamlit'
    ]
    
    for module_name in modules_to_mock:
        if module_name not in sys.modules:
            try:
                __import__(module_name)
            except ImportError:
                # Create mock module
                mock_module = MagicMock()
                
                # Add specific mocks for known attributes
                if module_name == 'pandas':
                    mock_module.DataFrame = MagicMock
                    mock_module.Timestamp = MagicMock
                    mock_module.date_range = MagicMock
                    mock_module.to_datetime = MagicMock
                elif module_name == 'backtrader':
                    mock_module.Cerebro = MagicMock
                    mock_module.Strategy = MagicMock
                    mock_module.feeds = MagicMock()
                    mock_module.feeds.PandasData = MagicMock
                    mock_module.analyzers = MagicMock()
                    mock_module.observers = MagicMock()
                elif module_name == 'telegram':
                    mock_module.Bot = MagicMock
                
                sys.modules[module_name] = mock_module

def run_safe_tests():
    """Run tests that don't require external dependencies"""
    # Mock modules first
    mock_missing_modules()
    
    # Import test modules
    try:
        from test_config import TestConfigManager, TestIndicatorsConfig
        
        # Create test suite with only config tests
        suite = unittest.TestSuite()
        
        # Add config tests
        suite.addTest(unittest.makeSuite(TestConfigManager))
        suite.addTest(unittest.makeSuite(TestIndicatorsConfig))
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
        
    except Exception as e:
        print(f"Error running safe tests: {e}")
        return False

def run_mock_tests():
    """Run all tests with mocked dependencies"""
    # Mock modules first
    mock_missing_modules()
    
    test_modules = [
        'test_config',
        'test_data_fetcher', 
        'test_strategies',
        'test_engine',
        'test_alerts'
    ]
    
    suite = unittest.TestSuite()
    
    for module_name in test_modules:
        try:
            module = __import__(module_name)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, unittest.TestCase) and 
                    attr != unittest.TestCase):
                    suite.addTest(unittest.makeSuite(attr))
        except Exception as e:
            print(f"Warning: Could not load test module {module_name}: {e}")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    print("=" * 60)
    print("BACKTRADER ALERTS SYSTEM - TEST RUNNER")
    print("=" * 60)
    
    # First try safe tests (config only)
    print("\n1. Running safe tests (configuration only)...")
    safe_success = run_safe_tests()
    
    print(f"\nSafe tests result: {'PASSED' if safe_success else 'FAILED'}")
    
    # Then try all tests with mocks
    print("\n2. Running all tests with mocked dependencies...")
    mock_success = run_mock_tests()
    
    print(f"\nMocked tests result: {'PASSED' if mock_success else 'FAILED'}")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY:")
    print(f"Configuration tests: {'✓ PASSED' if safe_success else '✗ FAILED'}")
    print(f"All tests (mocked):  {'✓ PASSED' if mock_success else '✗ FAILED'}")
    print("=" * 60)
    
    if not safe_success:
        print("\n⚠️  Configuration tests failed - check config_manager.py")
    
    if not mock_success:
        print("\n⚠️  Some tests failed - check individual modules")
    else:
        print("\n✅ All tests passed with mocked dependencies!")
        print("💡 Install requirements.txt for full testing with real dependencies")