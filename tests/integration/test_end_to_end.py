#!/usr/bin/env python3
"""
End-to-end integration test suite for the complete Backtrader Alerts System
"""
import unittest
import sys
import os
import pandas as pd
import numpy as np
import yaml
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))

class TestEndToEndWorkflows(unittest.TestCase):
    """Test complete end-to-end workflows"""
    
    def setUp(self):
        """Set up complete test environment"""
        self.create_test_config()
        self.create_test_data()
        
    def create_test_config(self):
        """Create complete test configuration"""
        self.config_data = {
            'trading': {
                'initial_cash': 10000,
                'commission': 0.001,
                'slippage': 0.0001
            },
            'data': {
                'default_source': 'yfinance',
                'default_interval': '1d'
            },
            'alerts': {
                'telegram': {
                    'enabled': False,  # Use console for testing
                    'bot_token': 'test_token',
                    'chat_id': 'test_chat'
                },
                'console': {
                    'enabled': True,
                    'log_to_file': True
                }
            },
            'strategies': {
                'rsi_crossover': {
                    'enabled': True,
                    'rsi_period': 14,
                    'rsi_oversold': 30,
                    'rsi_overbought': 70
                },
                'multi_indicator': {
                    'enabled': True,
                    'indicators': {
                        'RSI': {'period': 14},
                        'SMA': {'period': 20}
                    }
                },
                'multi_timeframe': {
                    'enabled': True,
                    'timeframes': ['1h', '4h', '1d']
                }
            }
        }
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(self.config_data, f)
            self.config_file = f.name
    
    def create_test_data(self):
        """Create realistic market data for testing"""
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        np.random.seed(42)
        
        # Generate realistic price data with trends and patterns
        base_price = 100
        prices = []
        current_price = base_price
        
        for i in range(len(dates)):
            # Create different market phases
            if i < 20:  # Downtrend
                trend = -0.5
            elif i < 40:  # Sideways
                trend = 0.1
            elif i < 70:  # Uptrend
                trend = 0.8
            else:  # Volatile
                trend = np.random.choice([-1, 1]) * 2.0
            
            change = np.random.normal(trend, 2.0)
            current_price *= (1 + change / 100)
            
            # Ensure realistic OHLC
            open_price = current_price * np.random.uniform(0.998, 1.002)
            high_price = max(open_price, current_price) * np.random.uniform(1.000, 1.005)
            low_price = min(open_price, current_price) * np.random.uniform(0.995, 1.000)
            volume = abs(np.random.normal(1000000, 200000))
            
            prices.append({
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': current_price,
                'volume': volume
            })
        
        self.market_data = pd.DataFrame(prices, index=dates)
        
        # Add technical indicators
        self.add_technical_indicators()
    
    def add_technical_indicators(self):
        """Add technical indicators to market data"""
        # RSI
        delta = self.market_data['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        self.market_data['rsi'] = 100 - (100 / (1 + rs))
        
        # Moving Averages
        self.market_data['sma_20'] = self.market_data['close'].rolling(window=20).mean()
        self.market_data['sma_50'] = self.market_data['close'].rolling(window=50).mean()
        
        # Bollinger Bands
        sma = self.market_data['close'].rolling(window=20).mean()
        std = self.market_data['close'].rolling(window=20).std()
        self.market_data['bb_upper'] = sma + (std * 2)
        self.market_data['bb_lower'] = sma - (std * 2)
    
    def tearDown(self):
        """Clean up test environment"""
        try:
            os.unlink(self.config_file)
        except:
            pass
    
    def test_complete_system_workflow(self):
        """Test complete system workflow from config to alerts"""
        print("\n🔄 Testing: Complete System Workflow")
        
        from src.config.config_manager import ConfigManager
        from src.alerts.console_dispatcher import ConsoleDispatcher
        
        # Step 1: Load Configuration
        config = ConfigManager(self.config_file)
        
        # Verify config loading
        assert config.get('trading.initial_cash') == 10000
        assert config.get('strategies.rsi_crossover.enabled') is True
        
        # Step 2: Initialize Alert System
        dispatcher = ConsoleDispatcher(log_to_file=True)
        
        # Step 3: Process Market Data and Generate Signals
        signals_generated = 0
        trades_executed = 0
        
        for i, (date, row) in enumerate(self.market_data.iterrows()):
            if i < 20:  # Skip initial period for indicators
                continue
                
            # RSI Strategy Signals
            if pd.notna(row['rsi']):
                if row['rsi'] < 30:  # Oversold
                    dispatcher.send_strategy_signal(
                        "RSI_Strategy", 
                        "BUY", 
                        "TEST-SYMBOL",
                        [f"RSI oversold: {row['rsi']:.1f}"]
                    )
                    signals_generated += 1
                    trades_executed += 1
                    
                elif row['rsi'] > 70:  # Overbought
                    dispatcher.send_strategy_signal(
                        "RSI_Strategy",
                        "SELL", 
                        "TEST-SYMBOL",
                        [f"RSI overbought: {row['rsi']:.1f}"]
                    )
                    signals_generated += 1
                    trades_executed += 1
            
            # Multi-Indicator Strategy
            if pd.notna(row['sma_20']) and pd.notna(row['sma_50']):
                if row['close'] > row['sma_20'] and row['sma_20'] > row['sma_50']:
                    dispatcher.send_strategy_signal(
                        "Multi_Indicator_Strategy",
                        "BUY",
                        "TEST-SYMBOL", 
                        ["Price > SMA20", "SMA20 > SMA50", "Bullish alignment"]
                    )
                    signals_generated += 1
        
        # Step 4: Verify End-to-End Results
        all_alerts = dispatcher.get_alerts_history()
        strategy_signals = dispatcher.get_alerts_by_type('strategy_signal')
        
        assert len(strategy_signals) > 0, "No strategy signals generated"
        assert signals_generated == len(strategy_signals), "Signal count mismatch"
        
        # Step 5: Performance Summary
        dispatcher.send_custom_alert(
            f"System Performance: {signals_generated} signals, {trades_executed} trades"
        )
        
        print(f"   Signals generated: {signals_generated}")
        print(f"   Trades executed: {trades_executed}")
        print(f"   Total alerts: {len(all_alerts)}")
        print("✅ Complete system workflow successful")
    
    def test_multi_strategy_coordination_e2e(self):
        """Test end-to-end multi-strategy coordination"""
        print("\n🎯 Testing: Multi-Strategy E2E Coordination")
        
        from src.alerts.console_dispatcher import ConsoleDispatcher
        
        dispatcher = ConsoleDispatcher()
        
        # Initialize multiple strategies with different approaches
        strategies = {
            'Momentum': {'signals': 0, 'threshold': 0.02},
            'Mean_Reversion': {'signals': 0, 'threshold': 0.05},
            'Trend_Following': {'signals': 0, 'threshold': 0.01}
        }
        
        # Process market data with multiple strategies
        for i in range(20, len(self.market_data)):
            row = self.market_data.iloc[i]
            prev_row = self.market_data.iloc[i-1]
            
            price_change = (row['close'] - prev_row['close']) / prev_row['close']
            
            # Momentum Strategy
            if abs(price_change) > strategies['Momentum']['threshold']:
                signal = "BUY" if price_change > 0 else "SELL"
                dispatcher.send_strategy_signal(
                    "Momentum_Strategy",
                    signal,
                    "MOMENTUM-TEST",
                    [f"Price momentum: {price_change:.2%}"]
                )
                strategies['Momentum']['signals'] += 1
            
            # Mean Reversion Strategy  
            if pd.notna(row['rsi']):
                if row['rsi'] < 25:  # Extreme oversold
                    dispatcher.send_strategy_signal(
                        "Mean_Reversion_Strategy",
                        "BUY",
                        "REVERSION-TEST",
                        [f"Extreme RSI: {row['rsi']:.1f}"]
                    )
                    strategies['Mean_Reversion']['signals'] += 1
                elif row['rsi'] > 75:  # Extreme overbought
                    dispatcher.send_strategy_signal(
                        "Mean_Reversion_Strategy", 
                        "SELL",
                        "REVERSION-TEST",
                        [f"Extreme RSI: {row['rsi']:.1f}"]
                    )
                    strategies['Mean_Reversion']['signals'] += 1
            
            # Trend Following Strategy
            if pd.notna(row['sma_20']) and pd.notna(row['sma_50']):
                if row['sma_20'] > row['sma_50'] and prev_row['sma_20'] <= prev_row['sma_50']:
                    dispatcher.send_strategy_signal(
                        "Trend_Following_Strategy",
                        "BUY", 
                        "TREND-TEST",
                        ["SMA crossover bullish"]
                    )
                    strategies['Trend_Following']['signals'] += 1
        
        # Verify multi-strategy coordination
        total_signals = sum(s['signals'] for s in strategies.values())
        strategy_alerts = dispatcher.get_alerts_by_type('strategy_signal')
        
        assert len(strategy_alerts) == total_signals, "Strategy signal count mismatch"
        
        # Check that each strategy generated signals
        active_strategies = len([s for s in strategies.values() if s['signals'] > 0])
        assert active_strategies > 1, "Multiple strategies should be active"
        
        print(f"   Active strategies: {active_strategies}/3")
        print(f"   Total signals: {total_signals}")
        print("✅ Multi-strategy E2E coordination successful")
    
    def test_error_handling_e2e(self):
        """Test end-to-end error handling"""
        print("\n🚨 Testing: End-to-End Error Handling")
        
        from src.config.config_manager import ConfigManager
        from src.alerts.console_dispatcher import ConsoleDispatcher
        from src.data.fetcher import DataFetcher
        
        dispatcher = ConsoleDispatcher()
        error_count = 0
        
        # Test configuration errors
        try:
            invalid_config = ConfigManager("nonexistent_file.yaml")
        except Exception:
            dispatcher.send_error_alert(
                "CONFIG_ERROR",
                "Configuration file not found",
                "test_error_handling_e2e"
            )
            error_count += 1
        
        # Test data fetcher errors
        fetcher = DataFetcher('yfinance')
        try:
            # This should handle missing dependencies gracefully
            result = fetcher.fetch_data('INVALID', '1d', '2023-01-01', '2023-01-31')
            if result is None:
                dispatcher.send_error_alert(
                    "DATA_ERROR",
                    "Failed to fetch data for invalid symbol",
                    "test_error_handling_e2e"
                )
                error_count += 1
        except ImportError:
            dispatcher.send_error_alert(
                "DEPENDENCY_ERROR", 
                "Required data dependency not available",
                "test_error_handling_e2e"
            )
            error_count += 1
        
        # Test strategy errors
        try:
            # Simulate invalid indicator calculation
            invalid_data = pd.DataFrame({'close': [None, None, None]})
            rsi = invalid_data['close'].rolling(14).mean()  # Will produce NaN
            if rsi.isna().all():
                dispatcher.send_error_alert(
                    "STRATEGY_ERROR",
                    "RSI calculation failed - insufficient data",
                    "test_error_handling_e2e"
                )
                error_count += 1
        except Exception as e:
            dispatcher.send_error_alert(
                "CALCULATION_ERROR",
                f"Indicator calculation error: {str(e)}",
                "test_error_handling_e2e"
            )
            error_count += 1
        
        # Test recovery
        dispatcher.send_custom_alert("System recovered - resuming normal operation")
        
        # Verify error handling
        error_alerts = dispatcher.get_alerts_by_type('error')
        recovery_alerts = [a for a in dispatcher.get_alerts_by_type('custom') 
                          if 'recovered' in a.get('message', '').lower()]
        
        assert len(error_alerts) > 0, "No error alerts generated"
        assert len(recovery_alerts) > 0, "No recovery alerts generated"
        assert error_count > 0, "No errors were handled"
        
        print(f"   Errors handled: {error_count}")
        print(f"   Error alerts: {len(error_alerts)}")
        print("✅ End-to-end error handling successful")
    
    def test_performance_monitoring_e2e(self):
        """Test end-to-end performance monitoring"""
        print("\n📊 Testing: E2E Performance Monitoring")
        
        from src.alerts.console_dispatcher import ConsoleDispatcher
        
        dispatcher = ConsoleDispatcher()
        
        # Simulate trading session with performance tracking
        session_start = datetime.now()
        initial_portfolio = 10000.0
        current_portfolio = initial_portfolio
        
        trades = []
        
        # Generate realistic trading scenario
        for i in range(20, min(50, len(self.market_data))):
            row = self.market_data.iloc[i]
            
            # Simple momentum strategy for testing
            if i > 20:
                prev_row = self.market_data.iloc[i-1]
                price_change = (row['close'] - prev_row['close']) / prev_row['close']
                
                if abs(price_change) > 0.02:  # Significant move
                    action = "BUY" if price_change > 0 else "SELL"
                    size = 100  # Fixed size for testing
                    trade_value = row['close'] * size
                    
                    if action == "BUY":
                        current_portfolio -= trade_value
                    else:
                        current_portfolio += trade_value
                    
                    trades.append({
                        'action': action,
                        'price': row['close'],
                        'size': size,
                        'value': trade_value,
                        'portfolio': current_portfolio
                    })
                    
                    dispatcher.send_alert(action, "PERF-TEST", row['close'], size)
        
        # Calculate performance metrics
        total_trades = len(trades)
        total_pnl = current_portfolio - initial_portfolio
        pnl_percent = (total_pnl / initial_portfolio) * 100
        
        # Send performance summary
        dispatcher.send_custom_alert(
            f"Trading Session Complete: {total_trades} trades, "
            f"P&L: ${total_pnl:.2f} ({pnl_percent:.2f}%)"
        )
        
        # System performance metrics
        session_duration = datetime.now() - session_start
        signals_per_second = total_trades / max(session_duration.total_seconds(), 1)
        
        dispatcher.send_custom_alert(
            f"System Performance: {signals_per_second:.2f} signals/sec, "
            f"Session duration: {session_duration.total_seconds():.1f}s"
        )
        
        # Verify performance monitoring
        trade_alerts = dispatcher.get_alerts_by_type('BUY') + dispatcher.get_alerts_by_type('SELL')
        performance_alerts = [a for a in dispatcher.get_alerts_by_type('custom')
                            if 'Performance' in a.get('message', '') or 'Session' in a.get('message', '')]
        
        assert len(trade_alerts) == total_trades, "Trade count mismatch"
        assert len(performance_alerts) >= 2, "Missing performance alerts"
        
        print(f"   Total trades: {total_trades}")
        print(f"   P&L: ${total_pnl:.2f} ({pnl_percent:.2f}%)")
        print(f"   System performance: {signals_per_second:.2f} signals/sec")
        print("✅ E2E performance monitoring successful")
    
    def test_system_scalability_e2e(self):
        """Test system scalability under load"""
        print("\n🚀 Testing: System Scalability E2E")
        
        from src.alerts.console_dispatcher import ConsoleDispatcher
        import time
        
        dispatcher = ConsoleDispatcher()
        
        # Test high-frequency alert generation
        start_time = time.time()
        alert_count = 0
        
        # Generate alerts rapidly
        for i in range(100):
            for strategy in ['FastScalp', 'QuickTrend', 'RapidMomentum']:
                dispatcher.send_strategy_signal(
                    strategy,
                    "BUY" if i % 2 == 0 else "SELL",
                    f"SYMBOL-{i % 10}",
                    [f"Signal {i}"]
                )
                alert_count += 1
        
        processing_time = time.time() - start_time
        alerts_per_second = alert_count / processing_time
        
        # Test alert history integrity under load
        history = dispatcher.get_alerts_history()
        
        # Test alert filtering performance
        filter_start = time.time()
        buy_alerts = dispatcher.get_alerts_by_type('strategy_signal')
        filter_time = time.time() - filter_start
        
        # Performance assertions
        assert len(history) == alert_count, "Alert history count mismatch"
        assert alerts_per_second > 100, "Alert processing too slow"
        assert filter_time < 1.0, "Alert filtering too slow"
        
        # Send scalability summary
        dispatcher.send_custom_alert(
            f"Scalability Test: {alert_count} alerts in {processing_time:.2f}s "
            f"({alerts_per_second:.0f} alerts/sec)"
        )
        
        print(f"   Alerts processed: {alert_count}")
        print(f"   Processing rate: {alerts_per_second:.0f} alerts/sec")
        print(f"   Filter time: {filter_time:.3f}s")
        print("✅ System scalability E2E successful")

class TestSystemIntegration(unittest.TestCase):
    """Test integration between all system components"""
    
    def test_component_integration_matrix(self):
        """Test integration between all major components"""
        print("\n🔧 Testing: Component Integration Matrix")
        
        # Test component imports and basic functionality
        components = {}
        
        try:
            from src.config.config_manager import ConfigManager
            components['ConfigManager'] = ConfigManager()
            components['ConfigManager'].set('test.key', 'test_value')
        except Exception as e:
            self.fail(f"ConfigManager integration failed: {e}")
        
        try:
            from src.data.fetcher import DataFetcher
            components['DataFetcher'] = DataFetcher('yfinance')
        except Exception as e:
            self.fail(f"DataFetcher integration failed: {e}")
        
        try:
            from src.alerts.console_dispatcher import ConsoleDispatcher
            components['ConsoleDispatcher'] = ConsoleDispatcher()
            components['ConsoleDispatcher'].test_connection()
        except Exception as e:
            self.fail(f"ConsoleDispatcher integration failed: {e}")
        
        # Test component interactions
        config = components['ConfigManager']
        dispatcher = components['ConsoleDispatcher']
        
        # Config -> Dispatcher integration
        alert_enabled = config.get('test.key', False)
        if alert_enabled:
            dispatcher.send_custom_alert("Integration test successful")
        
        integration_alerts = dispatcher.get_alerts_by_type('custom')
        
        assert len(components) >= 3, "Not all components loaded"
        assert len(integration_alerts) > 0, "Component integration failed"
        
        print(f"   Components integrated: {list(components.keys())}")
        print("✅ Component integration matrix successful")
    
    def test_data_flow_integration(self):
        """Test data flow between all components"""
        print("\n🌊 Testing: Data Flow Integration")
        
        from src.config.config_manager import ConfigManager
        from src.alerts.console_dispatcher import ConsoleDispatcher
        
        # Create data flow simulation
        config = ConfigManager()
        dispatcher = ConsoleDispatcher()
        
        # Stage 1: Configuration
        config.set('data.symbol', 'TEST-FLOW')
        config.set('data.interval', '1d')
        
        # Stage 2: Data Processing (simulated)
        test_data = {
            'symbol': config.get('data.symbol'),
            'interval': config.get('data.interval'),
            'records': 100,
            'indicators': ['RSI', 'SMA']
        }
        
        # Stage 3: Strategy Processing (simulated)
        strategy_results = {
            'signals_generated': 5,
            'buy_signals': 3,
            'sell_signals': 2
        }
        
        # Stage 4: Alert Generation
        for i in range(strategy_results['buy_signals']):
            dispatcher.send_alert('BUY', test_data['symbol'], 100 + i, 1.0)
        
        for i in range(strategy_results['sell_signals']):
            dispatcher.send_alert('SELL', test_data['symbol'], 105 + i, 1.0)
        
        # Stage 5: Verification
        all_alerts = dispatcher.get_alerts_history()
        buy_alerts = dispatcher.get_alerts_by_type('BUY')
        sell_alerts = dispatcher.get_alerts_by_type('SELL')
        
        # Data flow assertions
        assert len(buy_alerts) == strategy_results['buy_signals']
        assert len(sell_alerts) == strategy_results['sell_signals']
        assert len(all_alerts) == strategy_results['signals_generated']
        
        # Send flow summary
        dispatcher.send_custom_alert(
            f"Data flow: {test_data['symbol']} -> {len(all_alerts)} alerts"
        )
        
        print(f"   Data processed: {test_data['records']} records")
        print(f"   Signals generated: {strategy_results['signals_generated']}")
        print("✅ Data flow integration successful")

if __name__ == '__main__':
    print("="*60)
    print("INTEGRATION TESTS - END-TO-END WORKFLOWS")
    print("="*60)
    
    unittest.main(verbosity=2)