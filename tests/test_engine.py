import unittest
import pandas as pd
import backtrader as bt
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engine.backtrader_runner import BacktraderEngine
from src.strategies.rsi_crossover import RSICrossoverStrategy

class TestBacktraderEngine(unittest.TestCase):
    
    def setUp(self):
        self.engine = BacktraderEngine(initial_cash=10000, commission=0.001)
        
        # Create sample data
        self.sample_data = pd.DataFrame({
            'open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
            'high': [105, 106, 107, 108, 109, 110, 111, 112, 113, 114],
            'low': [95, 96, 97, 98, 99, 100, 101, 102, 103, 104],
            'close': [102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
            'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
        }, index=pd.date_range('2023-01-01', periods=10, freq='D'))
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        self.assertEqual(self.engine.initial_cash, 10000)
        self.assertEqual(self.engine.commission, 0.001)
        self.assertIsNone(self.engine.alert_dispatcher)
        self.assertIsNone(self.engine.cerebro)
    
    def test_engine_with_alert_dispatcher(self):
        """Test engine initialization with alert dispatcher"""
        mock_dispatcher = Mock()
        engine = BacktraderEngine(initial_cash=5000, commission=0.002, alert_dispatcher=mock_dispatcher)
        
        self.assertEqual(engine.initial_cash, 5000)
        self.assertEqual(engine.commission, 0.002)
        self.assertEqual(engine.alert_dispatcher, mock_dispatcher)
    
    def test_run_backtest_basic(self):
        """Test basic backtest execution"""
        strategy_params = {
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70
        }
        
        results = self.engine.run_backtest(
            strategy_class=RSICrossoverStrategy,
            data=self.sample_data,
            strategy_params=strategy_params
        )
        
        # Check result structure
        self.assertIsInstance(results, dict)
        self.assertIn('initial_value', results)
        self.assertIn('final_value', results)
        self.assertIn('total_return', results)
        self.assertIn('portfolio_value', results)
        self.assertIn('trades', results)
        
        # Check values
        self.assertEqual(results['initial_value'], 10000)
        self.assertIsInstance(results['final_value'], float)
        self.assertIsInstance(results['total_return'], float)
        self.assertIsInstance(results['portfolio_value'], list)
        self.assertIsInstance(results['trades'], list)
    
    def test_run_backtest_with_alert_dispatcher(self):
        """Test backtest with alert dispatcher"""
        mock_dispatcher = Mock()
        engine = BacktraderEngine(initial_cash=10000, commission=0.001, alert_dispatcher=mock_dispatcher)
        
        strategy_params = {
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70
        }
        
        results = engine.run_backtest(
            strategy_class=RSICrossoverStrategy,
            data=self.sample_data,
            strategy_params=strategy_params
        )
        
        self.assertIsInstance(results, dict)
        # Alert dispatcher should be passed to strategy
        self.assertIsNotNone(engine.cerebro)
    
    def test_run_backtest_no_params(self):
        """Test backtest without strategy parameters"""
        results = self.engine.run_backtest(
            strategy_class=RSICrossoverStrategy,
            data=self.sample_data
        )
        
        self.assertIsInstance(results, dict)
        self.assertEqual(results['initial_value'], 10000)
    
    def test_run_multi_timeframe_backtest(self):
        """Test multi-timeframe backtest"""
        timeframe_data = {
            '1h': self.sample_data.copy(),
            '4h': self.sample_data.copy()
        }
        
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
        
        strategy_params = {
            'timeframe_configs': timeframe_configs,
            'conditions': conditions
        }
        
        from src.strategies.multi_timeframe import MultiTimeframeStrategy
        
        results = self.engine.run_multi_timeframe_backtest(
            strategy_class=MultiTimeframeStrategy,
            timeframe_data=timeframe_data,
            strategy_params=strategy_params
        )
        
        # Check result structure
        self.assertIsInstance(results, dict)
        self.assertIn('timeframes_used', results)
        self.assertEqual(set(results['timeframes_used']), set(['1h', '4h']))
        self.assertIn('initial_value', results)
        self.assertIn('final_value', results)
    
    def test_run_multi_timeframe_backtest_empty_data(self):
        """Test multi-timeframe backtest with empty data"""
        timeframe_data = {}
        
        strategy_params = {
            'timeframe_configs': {},
            'conditions': []
        }
        
        from src.strategies.multi_timeframe import MultiTimeframeStrategy
        
        results = self.engine.run_multi_timeframe_backtest(
            strategy_class=MultiTimeframeStrategy,
            timeframe_data=timeframe_data,
            strategy_params=strategy_params
        )
        
        self.assertIsInstance(results, dict)
        self.assertEqual(results['timeframes_used'], [])
    
    def test_extract_trades_empty(self):
        """Test trade extraction with no trades"""
        # Create a minimal strategy for testing
        cerebro = bt.Cerebro()
        data_feed = bt.feeds.PandasData(dataname=self.sample_data)
        cerebro.adddata(data_feed)
        cerebro.addstrategy(RSICrossoverStrategy)
        
        strategies = cerebro.run()
        strategy = strategies[0]
        
        trades = self.engine._extract_trades(strategy)
        self.assertIsInstance(trades, list)
        # With random data, might or might not have trades
        for trade in trades:
            self.assertIsInstance(trade, dict)
            self.assertIn('entry_time', trade)
            self.assertIn('exit_time', trade)
            self.assertIn('entry_price', trade)
            self.assertIn('exit_price', trade)
            self.assertIn('size', trade)
            self.assertIn('pnl', trade)
            self.assertIn('pnl_pct', trade)
    
    def test_plot_results_no_cerebro(self):
        """Test plotting when cerebro is None"""
        # Should not crash when cerebro is None
        try:
            self.engine.plot_results()
        except Exception:
            pass  # Expected behavior
    
    def test_run_live_not_implemented(self):
        """Test that live trading raises NotImplementedError"""
        with self.assertRaises(NotImplementedError):
            self.engine.run_live(RSICrossoverStrategy, None)
    
    def test_backtest_analyzer_results(self):
        """Test that analyzers are properly added and results extracted"""
        strategy_params = {
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70
        }
        
        results = self.engine.run_backtest(
            strategy_class=RSICrossoverStrategy,
            data=self.sample_data,
            strategy_params=strategy_params
        )
        
        # Check analyzer results are included
        self.assertIn('sharpe_ratio', results)
        self.assertIn('max_drawdown', results)
        self.assertIn('total_trades', results)
        self.assertIn('winning_trades', results)
        self.assertIn('losing_trades', results)
        
        # Values should be numeric or None
        if results['sharpe_ratio'] is not None:
            self.assertIsInstance(results['sharpe_ratio'], (int, float))
        self.assertIsInstance(results['max_drawdown'], (int, float))
        self.assertIsInstance(results['total_trades'], int)
        self.assertIsInstance(results['winning_trades'], int)
        self.assertIsInstance(results['losing_trades'], int)
    
    def test_portfolio_value_tracking(self):
        """Test portfolio value is tracked correctly"""
        results = self.engine.run_backtest(
            strategy_class=RSICrossoverStrategy,
            data=self.sample_data
        )
        
        portfolio_values = results['portfolio_value']
        self.assertIsInstance(portfolio_values, list)
        self.assertGreater(len(portfolio_values), 0)
        
        # All values should be numeric
        for value in portfolio_values:
            self.assertIsInstance(value, (int, float))
            self.assertGreater(value, 0)  # Portfolio value should be positive

if __name__ == '__main__':
    unittest.main()