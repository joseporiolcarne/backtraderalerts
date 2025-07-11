#!/usr/bin/env python3
"""
Integration tests for strategy execution and alerts
"""
import unittest
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))

class MockBacktraderStrategy:
    """Mock strategy for testing without backtrader"""
    def __init__(self, **params):
        self.params = type('params', (), params)()
        self.alerts_sent = []
        self.trades_executed = []
        self.alert_dispatcher = None
        
    def set_alert_dispatcher(self, dispatcher):
        self.alert_dispatcher = dispatcher
        
    def simulate_trade(self, action, symbol, price, size=1.0):
        """Simulate a trade execution"""
        trade = {
            'action': action,
            'symbol': symbol,
            'price': price,
            'size': size,
            'timestamp': datetime.now()
        }
        self.trades_executed.append(trade)
        
        # Send alert if dispatcher available
        if self.alert_dispatcher:
            self.alert_dispatcher.send_alert(action, symbol, price, size)
        
        return trade

class TestStrategyExecution(unittest.TestCase):
    """Test strategy execution with alerts"""
    
    def setUp(self):
        """Set up test environment"""
        # Create sample market data
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        np.random.seed(42)
        
        # Generate trending data with RSI signals
        prices = []
        base_price = 100
        
        for i in range(len(dates)):
            # Create trend with some RSI oversold/overbought conditions
            if i < 20:
                change = -2.0  # Downtrend (should create oversold)
            elif i < 40:
                change = 0.1   # Sideways
            elif i < 60:
                change = 1.5   # Uptrend (should create overbought)
            else:
                change = np.random.normal(0, 1.0)  # Random
            
            base_price *= (1 + change / 100)
            
            prices.append({
                'open': base_price * 0.999,
                'high': base_price * 1.005,
                'low': base_price * 0.995,
                'close': base_price,
                'volume': 1000000
            })
        
        self.market_data = pd.DataFrame(prices, index=dates)
        
        # Calculate RSI for testing
        self._add_rsi_to_data()
    
    def _add_rsi_to_data(self):
        """Add RSI values to market data for testing"""
        closes = self.market_data['close']
        delta = closes.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        self.market_data['rsi'] = rsi
    
    def test_strategy_with_console_alerts(self):
        """Test strategy execution with console alerts"""
        print("\n📊 Testing: Strategy + Console Alerts")
        
        from src.alerts.console_dispatcher import ConsoleDispatcher
        
        # Create console dispatcher
        dispatcher = ConsoleDispatcher()
        
        # Create mock strategy
        strategy = MockBacktraderStrategy(
            rsi_period=14,
            rsi_oversold=30,
            rsi_overbought=70
        )
        strategy.set_alert_dispatcher(dispatcher)
        
        # Simulate strategy signals based on RSI
        trades_count = 0
        for i, (date, row) in enumerate(self.market_data.iterrows()):
            if pd.notna(row['rsi']):
                # Buy signal: RSI crosses above oversold
                if row['rsi'] > 30 and i > 0:
                    prev_rsi = self.market_data.iloc[i-1]['rsi']
                    if pd.notna(prev_rsi) and prev_rsi <= 30:
                        strategy.simulate_trade('BUY', 'TEST-SYMBOL', row['close'])
                        trades_count += 1
                
                # Sell signal: RSI crosses below overbought  
                if row['rsi'] < 70 and i > 0:
                    prev_rsi = self.market_data.iloc[i-1]['rsi']
                    if pd.notna(prev_rsi) and prev_rsi >= 70:
                        strategy.simulate_trade('SELL', 'TEST-SYMBOL', row['close'])
                        trades_count += 1
        
        # Verify alerts were sent
        alerts = dispatcher.get_alerts_history()
        assert len(alerts) > 0, "No alerts were sent"
        assert len(strategy.trades_executed) > 0, "No trades were executed"
        
        # Check alert types
        buy_alerts = dispatcher.get_alerts_by_type('BUY')
        sell_alerts = dispatcher.get_alerts_by_type('SELL')
        
        print(f"   Trades executed: {len(strategy.trades_executed)}")
        print(f"   Buy alerts: {len(buy_alerts)}")
        print(f"   Sell alerts: {len(sell_alerts)}")
        print(f"   Total alerts: {len(alerts)}")
        
        assert len(alerts) == len(strategy.trades_executed), "Mismatch between trades and alerts"
        
        print("✅ Strategy execution with console alerts working")
    
    def test_multi_strategy_coordination(self):
        """Test multiple strategies working together"""
        print("\n🔄 Testing: Multi-Strategy Coordination")
        
        from src.alerts.console_dispatcher import ConsoleDispatcher
        
        dispatcher = ConsoleDispatcher()
        
        # Create different strategies
        rsi_strategy = MockBacktraderStrategy(
            name="RSI_Strategy",
            rsi_period=14,
            rsi_oversold=30,
            rsi_overbought=70
        )
        rsi_strategy.set_alert_dispatcher(dispatcher)
        
        ma_strategy = MockBacktraderStrategy(
            name="MA_Strategy", 
            ma_period=20
        )
        ma_strategy.set_alert_dispatcher(dispatcher)
        
        # Simulate coordinated signals
        strategies = [rsi_strategy, ma_strategy]
        
        for i, strategy in enumerate(strategies):
            # Each strategy sends different types of signals
            strategy.simulate_trade('BUY' if i == 0 else 'SELL', 
                                  f'SYMBOL-{i}', 
                                  100 + i * 10)
        
        # Verify coordination
        alerts = dispatcher.get_alerts_history()
        assert len(alerts) == 2, "Expected 2 alerts from 2 strategies"
        
        # Check different symbols were used
        symbols = set(alert.get('symbol') for alert in alerts)
        assert len(symbols) == 2, "Strategies should use different symbols"
        
        print("✅ Multi-strategy coordination working")
    
    def test_strategy_error_handling(self):
        """Test strategy error handling and recovery"""
        print("\n🚨 Testing: Strategy Error Handling")
        
        from src.alerts.console_dispatcher import ConsoleDispatcher
        
        dispatcher = ConsoleDispatcher()
        
        # Simulate strategy errors
        dispatcher.send_error_alert(
            "STRATEGY_ERROR",
            "RSI calculation failed - insufficient data",
            "RSI Strategy initialization"
        )
        
        dispatcher.send_error_alert(
            "DATA_ERROR", 
            "Missing price data for 2023-01-15",
            "Data validation"
        )
        
        # Test error recovery
        dispatcher.send_custom_alert("Strategy recovered - resuming normal operation")
        
        # Verify error handling
        error_alerts = dispatcher.get_alerts_by_type('error')
        assert len(error_alerts) == 2, "Expected 2 error alerts"
        
        custom_alerts = dispatcher.get_alerts_by_type('custom')
        assert len(custom_alerts) == 1, "Expected 1 recovery alert"
        
        print("✅ Strategy error handling working")
    
    def test_strategy_performance_tracking(self):
        """Test strategy performance tracking"""
        print("\n📈 Testing: Strategy Performance Tracking")
        
        from src.alerts.console_dispatcher import ConsoleDispatcher
        
        dispatcher = ConsoleDispatcher()
        strategy = MockBacktraderStrategy(name="Performance_Test")
        strategy.set_alert_dispatcher(dispatcher)
        
        # Simulate a series of trades with P&L
        trades = [
            ('BUY', 'AAPL', 150.00, 1.0),
            ('SELL', 'AAPL', 155.00, 1.0),  # +$5 profit
            ('BUY', 'TSLA', 800.00, 0.5),
            ('SELL', 'TSLA', 790.00, 0.5),  # -$5 loss
            ('BUY', 'BTC-USD', 50000.00, 0.1),
            ('SELL', 'BTC-USD', 52000.00, 0.1),  # +$200 profit
        ]
        
        total_pnl = 0
        for action, symbol, price, size in trades:
            strategy.simulate_trade(action, symbol, price, size)
            
            # Calculate P&L for pairs
            if action == 'SELL':
                # Find corresponding BUY
                buy_trades = [t for t in strategy.trades_executed 
                             if t['action'] == 'BUY' and t['symbol'] == symbol]
                if buy_trades:
                    buy_price = buy_trades[-1]['price']
                    pnl = (price - buy_price) * size
                    total_pnl += pnl
                    
                    # Send performance alert
                    dispatcher.send_custom_alert(
                        f"Trade completed: {symbol} P&L: ${pnl:.2f}"
                    )
        
        # Send summary performance alert
        dispatcher.send_custom_alert(f"Total P&L: ${total_pnl:.2f}")
        
        # Verify performance tracking
        alerts = dispatcher.get_alerts_history()
        trade_alerts = [a for a in alerts if a.get('action') in ['BUY', 'SELL']]
        performance_alerts = [a for a in alerts if 'P&L' in a.get('message', '')]
        
        assert len(trade_alerts) == 6, "Expected 6 trade alerts"
        assert len(performance_alerts) > 0, "Expected performance alerts"
        
        print(f"   Total trades: {len(trade_alerts)}")
        print(f"   Performance alerts: {len(performance_alerts)}")
        print(f"   Total P&L: ${total_pnl:.2f}")
        
        print("✅ Strategy performance tracking working")

class TestRealTimeSimulation(unittest.TestCase):
    """Test real-time strategy simulation"""
    
    def test_real_time_alert_flow(self):
        """Test real-time alert flow simulation"""
        print("\n⏰ Testing: Real-Time Alert Flow")
        
        from src.alerts.console_dispatcher import ConsoleDispatcher
        import time
        
        dispatcher = ConsoleDispatcher()
        
        # Simulate real-time price updates and alerts
        prices = [100, 101, 99, 102, 98, 105, 95, 108]
        symbol = "BTC-USD"
        
        for i, price in enumerate(prices):
            # Simulate price-based alerts
            if i > 0:
                prev_price = prices[i-1]
                change_pct = ((price - prev_price) / prev_price) * 100
                
                if abs(change_pct) > 2:  # Significant price move
                    direction = "UP" if change_pct > 0 else "DOWN"
                    dispatcher.send_custom_alert(
                        f"Price Alert: {symbol} moved {direction} {abs(change_pct):.1f}% "
                        f"from ${prev_price:.2f} to ${price:.2f}"
                    )
            
            # Small delay to simulate real-time
            time.sleep(0.01)
        
        # Verify real-time alerts
        alerts = dispatcher.get_alerts_history()
        price_alerts = [a for a in alerts if 'Price Alert' in a.get('message', '')]
        
        assert len(price_alerts) > 0, "No price alerts generated"
        print(f"   Price alerts generated: {len(price_alerts)}")
        
        print("✅ Real-time alert flow working")
    
    def test_strategy_signal_aggregation(self):
        """Test aggregation of strategy signals"""
        print("\n📊 Testing: Strategy Signal Aggregation")
        
        from src.alerts.console_dispatcher import ConsoleDispatcher
        
        dispatcher = ConsoleDispatcher()
        
        # Simulate multiple strategy signals
        signals = [
            ("RSI_Strategy", "BUY", "BTC-USD", ["RSI < 30", "Volume spike"]),
            ("MACD_Strategy", "BUY", "BTC-USD", ["MACD crossover", "Bullish divergence"]),
            ("MA_Strategy", "NEUTRAL", "BTC-USD", ["Price near MA(50)"]),
            ("BB_Strategy", "SELL", "ETH-USD", ["Price above upper band", "High volatility"])
        ]
        
        for strategy, signal, symbol, conditions in signals:
            dispatcher.send_strategy_signal(strategy, signal, symbol, conditions)
        
        # Analyze signal aggregation
        strategy_alerts = dispatcher.get_alerts_by_type('strategy_signal')
        assert len(strategy_alerts) == 4, "Expected 4 strategy signals"
        
        # Group by symbol
        btc_signals = [s for s in strategy_alerts if s.get('symbol') == 'BTC-USD']
        eth_signals = [s for s in strategy_alerts if s.get('symbol') == 'ETH-USD']
        
        assert len(btc_signals) == 3, "Expected 3 BTC signals"
        assert len(eth_signals) == 1, "Expected 1 ETH signal"
        
        # Check signal consensus
        btc_buy_signals = [s for s in btc_signals if s.get('signal') == 'BUY']
        print(f"   BTC consensus: {len(btc_buy_signals)}/3 strategies bullish")
        
        print("✅ Strategy signal aggregation working")

class TestAlertReliability(unittest.TestCase):
    """Test alert system reliability"""
    
    def test_alert_delivery_reliability(self):
        """Test alert delivery under various conditions"""
        print("\n🔔 Testing: Alert Delivery Reliability")
        
        from src.alerts.console_dispatcher import ConsoleDispatcher
        
        dispatcher = ConsoleDispatcher()
        
        # Test various alert types
        alert_tests = [
            ('send_alert', ['BUY', 'AAPL', 150.50, 10]),
            ('send_custom_alert', ['Custom message test']),
            ('send_strategy_signal', ['TestStrategy', 'BUY', 'AAPL', ['Condition 1']]),
            ('send_error_alert', ['TEST_ERROR', 'Test error message']),
        ]
        
        for method_name, args in alert_tests:
            method = getattr(dispatcher, method_name)
            try:
                method(*args)
            except Exception as e:
                self.fail(f"Alert method {method_name} failed: {e}")
        
        # Verify all alerts were delivered
        total_alerts = len(dispatcher.get_alerts_history())
        assert total_alerts == 4, f"Expected 4 alerts, got {total_alerts}"
        
        print("✅ Alert delivery reliability confirmed")
    
    def test_alert_history_integrity(self):
        """Test alert history maintains integrity"""
        print("\n📚 Testing: Alert History Integrity")
        
        from src.alerts.console_dispatcher import ConsoleDispatcher
        
        dispatcher = ConsoleDispatcher()
        
        # Send series of alerts
        for i in range(10):
            dispatcher.send_alert('BUY' if i % 2 == 0 else 'SELL', 
                                f'SYMBOL-{i}', 100 + i, 1.0)
        
        # Verify history integrity
        history = dispatcher.get_alerts_history()
        assert len(history) == 10, "History count mismatch"
        
        # Verify chronological order
        timestamps = [alert['timestamp'] for alert in history]
        assert timestamps == sorted(timestamps), "Alerts not in chronological order"
        
        # Test filtering
        buy_alerts = dispatcher.get_alerts_by_type('BUY')
        sell_alerts = dispatcher.get_alerts_by_type('SELL')
        
        assert len(buy_alerts) == 5, "Expected 5 BUY alerts"
        assert len(sell_alerts) == 5, "Expected 5 SELL alerts"
        
        # Test export functionality
        export_file = dispatcher.export_alerts('test_export.json')
        assert export_file is not None, "Export failed"
        
        # Cleanup
        try:
            os.remove(export_file)
        except:
            pass
        
        print("✅ Alert history integrity confirmed")

if __name__ == '__main__':
    print("="*60)
    print("INTEGRATION TESTS - STRATEGY EXECUTION")
    print("="*60)
    
    unittest.main(verbosity=2)