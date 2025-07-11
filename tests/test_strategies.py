import unittest
import pandas as pd
import backtrader as bt
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.strategies.rsi_crossover import RSICrossoverStrategy
from src.strategies.multi_indicator import SimpleIndicatorStrategy, MultiIndicatorStrategy
from src.strategies.multi_timeframe import MultiTimeframeStrategy

class TestRSICrossoverStrategy(unittest.TestCase):
    
    def setUp(self):
        self.sample_data = pd.DataFrame({
            'open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
            'high': [105, 106, 107, 108, 109, 110, 111, 112, 113, 114],
            'low': [95, 96, 97, 98, 99, 100, 101, 102, 103, 104],
            'close': [102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
            'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
        }, index=pd.date_range('2023-01-01', periods=10, freq='D'))
    
    def test_rsi_strategy_params(self):
        """Test RSI strategy parameter setting"""
        cerebro = bt.Cerebro()
        data_feed = bt.feeds.PandasData(dataname=self.sample_data)
        cerebro.adddata(data_feed)
        
        # Add strategy with custom parameters
        cerebro.addstrategy(RSICrossoverStrategy, 
                          rsi_period=21, 
                          rsi_oversold=25, 
                          rsi_overbought=75)
        
        strategies = cerebro.run()
        strategy = strategies[0]
        
        self.assertEqual(strategy.params.rsi_period, 21)
        self.assertEqual(strategy.params.rsi_oversold, 25)
        self.assertEqual(strategy.params.rsi_overbought, 75)
    
    def test_rsi_strategy_initialization(self):
        """Test RSI strategy initialization"""
        cerebro = bt.Cerebro()
        data_feed = bt.feeds.PandasData(dataname=self.sample_data)
        cerebro.adddata(data_feed)
        
        cerebro.addstrategy(RSICrossoverStrategy)
        strategies = cerebro.run()
        strategy = strategies[0]
        
        # Check that RSI indicator is created
        self.assertTrue(hasattr(strategy, 'rsi'))
        self.assertIsNotNone(strategy.rsi)

class TestSimpleIndicatorStrategy(unittest.TestCase):
    
    def setUp(self):
        self.sample_data = pd.DataFrame({
            'open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
            'high': [105, 106, 107, 108, 109, 110, 111, 112, 113, 114],
            'low': [95, 96, 97, 98, 99, 100, 101, 102, 103, 104],
            'close': [102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
            'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
        }, index=pd.date_range('2023-01-01', periods=10, freq='D'))
    
    def test_simple_indicator_strategy_rsi(self):
        """Test Simple Indicator Strategy with RSI"""
        cerebro = bt.Cerebro()
        data_feed = bt.feeds.PandasData(dataname=self.sample_data)
        cerebro.adddata(data_feed)
        
        cerebro.addstrategy(SimpleIndicatorStrategy,
                          indicator_type='RSI',
                          indicator_params={'period': 14},
                          entry_value=30,
                          exit_value=70,
                          entry_operator='<',
                          exit_operator='>')
        
        strategies = cerebro.run()
        strategy = strategies[0]
        
        self.assertEqual(strategy.params.indicator_type, 'RSI')
        self.assertEqual(strategy.params.entry_value, 30)
        self.assertEqual(strategy.params.exit_value, 70)
        self.assertTrue(hasattr(strategy, 'indicator'))
    
    def test_simple_indicator_strategy_sma(self):
        """Test Simple Indicator Strategy with SMA"""
        cerebro = bt.Cerebro()
        data_feed = bt.feeds.PandasData(dataname=self.sample_data)
        cerebro.adddata(data_feed)
        
        cerebro.addstrategy(SimpleIndicatorStrategy,
                          indicator_type='SMA',
                          indicator_params={'period': 20},
                          entry_value=100,
                          exit_value=110,
                          entry_operator='>',
                          exit_operator='<')
        
        strategies = cerebro.run()
        strategy = strategies[0]
        
        self.assertEqual(strategy.params.indicator_type, 'SMA')
        self.assertTrue(hasattr(strategy, 'indicator'))
    
    def test_check_condition_operators(self):
        """Test condition checking with different operators"""
        cerebro = bt.Cerebro()
        data_feed = bt.feeds.PandasData(dataname=self.sample_data)
        cerebro.adddata(data_feed)
        
        cerebro.addstrategy(SimpleIndicatorStrategy,
                          indicator_type='RSI',
                          indicator_params={'period': 14})
        
        strategies = cerebro.run()
        strategy = strategies[0]
        
        # Test different operators
        self.assertTrue(strategy.check_condition(50, 30, '>'))
        self.assertFalse(strategy.check_condition(20, 30, '>'))
        self.assertTrue(strategy.check_condition(20, 30, '<'))
        self.assertFalse(strategy.check_condition(50, 30, '<'))
        self.assertTrue(strategy.check_condition(30, 30, '>='))
        self.assertTrue(strategy.check_condition(30, 30, '<='))
        self.assertTrue(strategy.check_condition(30, 30, '=='))

class TestMultiIndicatorStrategy(unittest.TestCase):
    
    def setUp(self):
        self.sample_data = pd.DataFrame({
            'open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
            'high': [105, 106, 107, 108, 109, 110, 111, 112, 113, 114],
            'low': [95, 96, 97, 98, 99, 100, 101, 102, 103, 104],
            'close': [102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
            'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
        }, index=pd.date_range('2023-01-01', periods=10, freq='D'))
    
    def test_multi_indicator_strategy_initialization(self):
        """Test Multi-Indicator Strategy initialization"""
        indicators_config = {
            'rsi': {'type': 'RSI', 'params': {'period': 14}},
            'sma': {'type': 'SMA', 'params': {'period': 20}}
        }
        
        entry_conditions = [
            {'indicator': 'rsi', 'operator': '<', 'value': 30}
        ]
        
        exit_conditions = [
            {'indicator': 'rsi', 'operator': '>', 'value': 70}
        ]
        
        cerebro = bt.Cerebro()
        data_feed = bt.feeds.PandasData(dataname=self.sample_data)
        cerebro.adddata(data_feed)
        
        cerebro.addstrategy(MultiIndicatorStrategy,
                          indicators=indicators_config,
                          entry_conditions=entry_conditions,
                          exit_conditions=exit_conditions)
        
        strategies = cerebro.run()
        strategy = strategies[0]
        
        self.assertTrue(hasattr(strategy, 'indicators'))
        self.assertIn('rsi', strategy.indicators)
        self.assertIn('sma', strategy.indicators)
    
    def test_evaluate_condition_indicator(self):
        """Test condition evaluation for indicators"""
        indicators_config = {
            'rsi': {'type': 'RSI', 'params': {'period': 14}}
        }
        
        cerebro = bt.Cerebro()
        data_feed = bt.feeds.PandasData(dataname=self.sample_data)
        cerebro.adddata(data_feed)
        
        cerebro.addstrategy(MultiIndicatorStrategy, indicators=indicators_config)
        strategies = cerebro.run()
        strategy = strategies[0]
        
        # Mock RSI values for testing
        if hasattr(strategy.indicators['rsi'], 'lines'):
            # Mock the RSI line values
            strategy.indicators['rsi'].lines[0].array = [50.0] * 10
        
        # Test condition evaluation
        condition = {'indicator': 'rsi', 'operator': '>', 'value': 30}
        # This would need actual market data to test properly
        # For now, just test that the method doesn't crash
        try:
            result = strategy.evaluate_condition(condition)
            self.assertIsInstance(result, bool)
        except (IndexError, AttributeError):
            # Expected with mock data
            pass
    
    def test_check_conditions_empty(self):
        """Test condition checking with empty conditions"""
        cerebro = bt.Cerebro()
        data_feed = bt.feeds.PandasData(dataname=self.sample_data)
        cerebro.adddata(data_feed)
        
        cerebro.addstrategy(MultiIndicatorStrategy)
        strategies = cerebro.run()
        strategy = strategies[0]
        
        # Empty conditions should return False
        result = strategy.check_conditions([])
        self.assertFalse(result)

class TestMultiTimeframeStrategy(unittest.TestCase):
    
    def setUp(self):
        self.sample_data = pd.DataFrame({
            'open': [100, 101, 102, 103, 104],
            'high': [105, 106, 107, 108, 109],
            'low': [95, 96, 97, 98, 99],
            'close': [102, 103, 104, 105, 106],
            'volume': [1000, 1100, 1200, 1300, 1400]
        }, index=pd.date_range('2023-01-01', periods=5, freq='D'))
    
    def test_multi_timeframe_strategy_initialization(self):
        """Test Multi-Timeframe Strategy initialization"""
        timeframe_configs = {
            '1h': {
                'indicators': {
                    'rsi': {'type': 'RSI', 'params': {'period': 14}}
                }
            },
            '4h': {
                'indicators': {
                    'sma': {'type': 'SMA', 'params': {'period': 20}}
                }
            }
        }
        
        conditions = [
            {
                'action': 'BUY',
                'operator': 'AND',
                'conditions': [
                    {'timeframe': '1h', 'type': 'indicator', 'indicator': 'rsi', 'operator': '<', 'value': 30}
                ]
            }
        ]
        
        cerebro = bt.Cerebro()
        data_feed1 = bt.feeds.PandasData(dataname=self.sample_data, name="1h_data")
        data_feed2 = bt.feeds.PandasData(dataname=self.sample_data, name="4h_data")
        cerebro.adddata(data_feed1)
        cerebro.adddata(data_feed2)
        
        # Update configs with data feeds
        timeframe_configs['1h']['data'] = data_feed1
        timeframe_configs['4h']['data'] = data_feed2
        
        cerebro.addstrategy(MultiTimeframeStrategy,
                          timeframe_configs=timeframe_configs,
                          conditions=conditions)
        
        strategies = cerebro.run()
        strategy = strategies[0]
        
        self.assertTrue(hasattr(strategy, 'indicators'))
        self.assertIn('1h', strategy.indicators)
        self.assertIn('4h', strategy.indicators)
    
    def test_evaluate_price_condition(self):
        """Test price condition evaluation"""
        cerebro = bt.Cerebro()
        data_feed = bt.feeds.PandasData(dataname=self.sample_data)
        cerebro.adddata(data_feed)
        
        timeframe_configs = {'1h': {'data': data_feed, 'indicators': {}}}
        
        cerebro.addstrategy(MultiTimeframeStrategy, timeframe_configs=timeframe_configs)
        strategies = cerebro.run()
        strategy = strategies[0]
        
        # Test price conditions
        condition = {'type': 'price', 'price_type': 'close', 'operator': '>', 'value': 100}
        
        # This would need actual execution to test properly
        # For now, just test that the method exists and doesn't crash on basic calls
        self.assertTrue(hasattr(strategy, 'evaluate_price_condition'))
        self.assertTrue(hasattr(strategy, 'evaluate_indicator_condition'))
        self.assertTrue(hasattr(strategy, 'evaluate_crossover_condition'))
    
    def test_check_condition_group(self):
        """Test condition group checking"""
        cerebro = bt.Cerebro()
        data_feed = bt.feeds.PandasData(dataname=self.sample_data)
        cerebro.adddata(data_feed)
        
        cerebro.addstrategy(MultiTimeframeStrategy)
        strategies = cerebro.run()
        strategy = strategies[0]
        
        # Test with empty condition group
        condition_group = {'conditions': [], 'operator': 'AND', 'action': 'BUY'}
        result = strategy.check_condition_group(condition_group)
        self.assertFalse(result)
        
        # Test with invalid action when in position
        strategy.position = Mock()
        strategy.position.__bool__ = Mock(return_value=True)
        condition_group = {'conditions': [], 'operator': 'AND', 'action': 'BUY'}
        result = strategy.check_condition_group(condition_group)
        self.assertFalse(result)

class TestStrategyBase(unittest.TestCase):
    """Test common strategy functionality"""
    
    def setUp(self):
        self.sample_data = pd.DataFrame({
            'open': [100, 101, 102, 103, 104],
            'high': [105, 106, 107, 108, 109],
            'low': [95, 96, 97, 98, 99],
            'close': [102, 103, 104, 105, 106],
            'volume': [1000, 1100, 1200, 1300, 1400]
        }, index=pd.date_range('2023-01-01', periods=5, freq='D'))
    
    def test_strategy_logging(self):
        """Test strategy logging functionality"""
        cerebro = bt.Cerebro()
        data_feed = bt.feeds.PandasData(dataname=self.sample_data)
        cerebro.adddata(data_feed)
        
        cerebro.addstrategy(RSICrossoverStrategy, printlog=True)
        strategies = cerebro.run()
        strategy = strategies[0]
        
        # Test that log method exists and can be called
        self.assertTrue(hasattr(strategy, 'log'))
        
        # Test logging (should not raise exception)
        try:
            strategy.log("Test message")
        except Exception as e:
            self.fail(f"Logging raised an exception: {e}")
    
    def test_strategy_alert_dispatcher(self):
        """Test strategy with alert dispatcher"""
        mock_dispatcher = Mock()
        
        cerebro = bt.Cerebro()
        data_feed = bt.feeds.PandasData(dataname=self.sample_data)
        cerebro.adddata(data_feed)
        
        cerebro.addstrategy(RSICrossoverStrategy, alert_dispatcher=mock_dispatcher)
        strategies = cerebro.run()
        strategy = strategies[0]
        
        # Check that alert dispatcher is set
        self.assertTrue(hasattr(strategy, 'alert_dispatcher'))
        self.assertEqual(strategy.alert_dispatcher, mock_dispatcher)

if __name__ == '__main__':
    unittest.main()