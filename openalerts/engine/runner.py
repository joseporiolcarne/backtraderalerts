import backtrader as bt
import pandas as pd
from typing import Dict, Any, List, Optional, Type
from ..alerts.telegram import TelegramDispatcher, send_telegram
from ..strategies.rsi_crossover import RSICrossover, MultiIndicatorAlert
import os
from datetime import datetime


class AlertCerebro(bt.Cerebro):
    """Extended Cerebro with alert capabilities"""
    def __init__(self):
        super().__init__()
        self.telegram_messages = []


def run_strategy(
    dataframe: pd.DataFrame,
    strategy_cls: Type[bt.Strategy],
    strategy_config: Dict[str, Any],
    telegram_conf: Optional[Dict[str, str]] = None,
    initial_cash: float = 10000.0,
    commission: float = 0.001,
    live_mode: bool = False
) -> Dict[str, Any]:
    """
    Run a backtrader strategy with alert capabilities
    
    Args:
        dataframe: OHLCV data
        strategy_cls: Backtrader strategy class
        strategy_config: Strategy parameters
        telegram_conf: Telegram configuration (token, chat_id)
        initial_cash: Starting cash for backtesting
        commission: Commission rate
        live_mode: Whether to run in live mode (True) or backtest (False)
    
    Returns:
        Dictionary with results and alerts
    """
    
    # Create custom cerebro instance
    cerebro = AlertCerebro()
    
    # Add data feed
    data = bt.feeds.PandasData(
        dataname=dataframe,
        datetime=None,  # Use index as datetime
        open='open',
        high='high',
        low='low',
        close='close',
        volume='volume',
        openinterest=None
    )
    cerebro.adddata(data)
    
    # Add strategy with config
    cerebro.addstrategy(strategy_cls, **strategy_config)
    
    # Set up broker
    cerebro.broker.setcash(initial_cash)
    cerebro.broker.setcommission(commission=commission)
    
    # Add analyzers for backtesting
    if not live_mode:
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    
    # Run strategy
    print(f"Starting {'live' if live_mode else 'backtest'} run...")
    start_value = cerebro.broker.getvalue()
    results = cerebro.run()
    end_value = cerebro.broker.getvalue()
    
    # Process alerts
    alerts_sent = 0
    if telegram_conf and telegram_conf.get('token') and telegram_conf.get('chat_id'):
        dispatcher = TelegramDispatcher(
            bot_token=telegram_conf['token'],
            chat_id=telegram_conf['chat_id']
        )
        
        for msg in cerebro.telegram_messages:
            if dispatcher.send_message(msg):
                alerts_sent += 1
    
    # Prepare results
    result_dict = {
        'start_value': start_value,
        'end_value': end_value,
        'profit': end_value - start_value,
        'profit_pct': ((end_value - start_value) / start_value) * 100,
        'alerts_generated': len(cerebro.telegram_messages),
        'alerts_sent': alerts_sent,
        'messages': cerebro.telegram_messages
    }
    
    # Add analyzer results for backtesting
    if not live_mode and results[0].analyzers:
        strat = results[0]
        result_dict['sharpe_ratio'] = strat.analyzers.sharpe.get_analysis().get('sharperatio', 0)
        
        drawdown = strat.analyzers.drawdown.get_analysis()
        result_dict['max_drawdown'] = drawdown.get('max', {}).get('drawdown', 0)
        
        returns = strat.analyzers.returns.get_analysis()
        result_dict['total_return'] = returns.get('rtot', 0)
        
        trades = strat.analyzers.trades.get_analysis()
        result_dict['total_trades'] = trades.get('total', {}).get('total', 0)
    
    return result_dict


def run_live_monitoring(
    symbols: List[str],
    strategy_cls: Type[bt.Strategy],
    strategy_config: Dict[str, Any],
    telegram_conf: Dict[str, str],
    fetch_func,
    timeframe: str = '1h',
    lookback: int = 100,
    interval_seconds: int = 300
):
    """
    Run continuous monitoring with periodic data updates
    
    Args:
        symbols: List of symbols to monitor
        strategy_cls: Strategy class to use
        strategy_config: Strategy parameters
        telegram_conf: Telegram configuration
        fetch_func: Function to fetch data
        timeframe: Timeframe for data
        lookback: Number of bars to analyze
        interval_seconds: Seconds between updates
    """
    import time
    
    print(f"Starting live monitoring for {symbols}")
    print(f"Update interval: {interval_seconds} seconds")
    
    while True:
        try:
            for symbol in symbols:
                print(f"\nChecking {symbol}...")
                
                # Fetch latest data
                df = fetch_func(symbol, timeframe, lookback)
                
                if df.empty:
                    print(f"No data received for {symbol}")
                    continue
                
                # Update strategy config with symbol
                config = strategy_config.copy()
                config['symbol'] = symbol
                
                # Run strategy
                results = run_strategy(
                    dataframe=df,
                    strategy_cls=strategy_cls,
                    strategy_config=config,
                    telegram_conf=telegram_conf,
                    live_mode=True
                )
                
                if results['alerts_generated'] > 0:
                    print(f"Generated {results['alerts_generated']} alerts for {symbol}")
            
            print(f"\nSleeping for {interval_seconds} seconds...")
            time.sleep(interval_seconds)
            
        except KeyboardInterrupt:
            print("\nStopping live monitoring...")
            break
        except Exception as e:
            print(f"Error in live monitoring: {e}")
            time.sleep(60)  # Wait a minute before retrying


def backtest_strategy(
    symbol: str,
    strategy_cls: Type[bt.Strategy],
    strategy_config: Dict[str, Any],
    fetch_func,
    timeframe: str = '1d',
    lookback: int = 365,
    plot: bool = False
) -> Dict[str, Any]:
    """
    Run a backtest on historical data
    
    Args:
        symbol: Symbol to test
        strategy_cls: Strategy class
        strategy_config: Strategy parameters
        fetch_func: Data fetching function
        timeframe: Timeframe for data
        lookback: Number of bars to test
        plot: Whether to generate plot
    
    Returns:
        Backtest results
    """
    print(f"Backtesting {symbol} with {lookback} {timeframe} bars")
    
    # Fetch historical data
    df = fetch_func(symbol, timeframe, lookback)
    
    if df.empty:
        return {'error': 'No data available'}
    
    # Add symbol to config
    config = strategy_config.copy()
    config['symbol'] = symbol
    
    # Run backtest
    results = run_strategy(
        dataframe=df,
        strategy_cls=strategy_cls,
        strategy_config=config,
        telegram_conf=None,  # No alerts in backtest
        live_mode=False
    )
    
    print(f"\nBacktest Results:")
    print(f"Profit: ${results['profit']:.2f} ({results['profit_pct']:.2f}%)")
    print(f"Sharpe Ratio: {results.get('sharpe_ratio', 0):.2f}")
    print(f"Max Drawdown: {results.get('max_drawdown', 0):.2f}%")
    print(f"Total Trades: {results.get('total_trades', 0)}")
    print(f"Alerts Generated: {results['alerts_generated']}")
    
    return results