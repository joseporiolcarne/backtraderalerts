#!/usr/bin/env python3
"""
Backtrader Alerts System - Main Runner
"""

import argparse
import sys
from datetime import datetime, timedelta
from src.config.config_manager import ConfigManager
from src.data.fetcher import DataFetcher
from src.alerts.telegram_dispatcher import TelegramDispatcher
from src.engine.backtrader_runner import BacktraderEngine
from src.strategies.rsi_crossover import RSICrossoverStrategy
from src.strategies.multi_indicator import SimpleIndicatorStrategy, MultiIndicatorStrategy

def run_cli():
    parser = argparse.ArgumentParser(description='Backtrader Alerts System - CLI')
    parser.add_argument('--mode', choices=['backtest', 'gui'], default='gui',
                        help='Run mode: backtest or gui (default: gui)')
    
    # Backtest arguments
    parser.add_argument('--symbol', type=str, help='Trading symbol (e.g., BTC-USD)')
    parser.add_argument('--interval', type=str, help='Time interval (e.g., 1d, 4h, 1h)')
    parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--data-source', choices=['yfinance', 'binance'], help='Data source')
    
    # Strategy parameters
    parser.add_argument('--rsi-period', type=int, help='RSI period')
    parser.add_argument('--rsi-oversold', type=int, help='RSI oversold level')
    parser.add_argument('--rsi-overbought', type=int, help='RSI overbought level')
    
    # Trading parameters
    parser.add_argument('--initial-cash', type=float, help='Initial cash amount')
    parser.add_argument('--commission', type=float, help='Commission rate (0-1)')
    
    # Config file
    parser.add_argument('--config', type=str, help='Path to config file')
    
    args = parser.parse_args()
    
    # Load configuration
    config = ConfigManager(args.config)
    
    if args.mode == 'gui':
        # Launch Streamlit GUI
        import subprocess
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'src/gui/streamlit_app.py'])
    else:
        # Run backtest from CLI
        run_backtest_cli(args, config)

def run_backtest_cli(args, config):
    """Run backtest from command line"""
    
    # Get parameters from args or config
    symbol = args.symbol or config.get('backtest.default_symbol')
    interval = args.interval or config.get('backtest.default_interval')
    data_source = args.data_source or config.get('data.default_source')
    
    # Date handling
    if args.end_date:
        end_date = args.end_date
    else:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    if args.start_date:
        start_date = args.start_date
    else:
        lookback_days = config.get('backtest.default_lookback_days', 365)
        start_date = (datetime.now() - timedelta(days=lookback_days)).strftime('%Y-%m-%d')
    
    # Strategy parameters
    strategy_params = {
        'rsi_period': args.rsi_period or config.get('strategies.rsi_crossover.rsi_period'),
        'rsi_oversold': args.rsi_oversold or config.get('strategies.rsi_crossover.rsi_oversold'),
        'rsi_overbought': args.rsi_overbought or config.get('strategies.rsi_crossover.rsi_overbought')
    }
    
    # Trading parameters
    initial_cash = args.initial_cash or config.get('trading.initial_cash')
    commission = args.commission or config.get('trading.commission')
    
    print(f"Running backtest for {symbol}")
    print(f"Period: {start_date} to {end_date}")
    print(f"Interval: {interval}")
    print(f"Data source: {data_source}")
    print(f"Strategy parameters: {strategy_params}")
    print("-" * 50)
    
    # Initialize components
    fetcher = DataFetcher(data_source=data_source)
    
    # Fetch data
    print("Fetching data...")
    df = fetcher.fetch_data(symbol, interval, start_date, end_date)
    
    if df is None or df.empty:
        print("Error: Failed to fetch data")
        return
    
    print(f"Data fetched: {len(df)} bars")
    
    # Initialize Telegram dispatcher if configured
    dispatcher = None
    if config.get('telegram.bot_token') and config.get('telegram.chat_id'):
        print("Initializing Telegram alerts...")
        dispatcher = TelegramDispatcher(
            config.get('telegram.bot_token'),
            config.get('telegram.chat_id')
        )
    
    # Run backtest
    print("Running backtest...")
    engine = BacktraderEngine(
        initial_cash=initial_cash,
        commission=commission,
        alert_dispatcher=dispatcher
    )
    
    results = engine.run_backtest(
        strategy_class=RSICrossoverStrategy,
        data=df,
        strategy_params=strategy_params
    )
    
    # Display results
    print("\n" + "=" * 50)
    print("BACKTEST RESULTS")
    print("=" * 50)
    
    final_value = results['portfolio_value'][-1] if results['portfolio_value'] else initial_cash
    total_return = ((final_value - initial_cash) / initial_cash) * 100
    
    print(f"Initial Cash: ${initial_cash:,.2f}")
    print(f"Final Portfolio Value: ${final_value:,.2f}")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Total Trades: {len(results['trades'])}")
    
    if results['trades']:
        winning_trades = sum(1 for t in results['trades'] if t.get('pnl', 0) > 0)
        win_rate = (winning_trades / len(results['trades'])) * 100
        print(f"Win Rate: {win_rate:.2f}%")
        
        # Show recent trades
        print("\nRecent Trades:")
        print("-" * 80)
        print(f"{'Entry Time':<20} {'Exit Time':<20} {'Size':<10} {'PnL':<10} {'PnL %':<10}")
        print("-" * 80)
        
        for trade in results['trades'][-5:]:  # Last 5 trades
            entry_time = trade.get('entry_time', 'N/A')
            exit_time = trade.get('exit_time', 'N/A')
            size = trade.get('size', 0)
            pnl = trade.get('pnl', 0)
            pnl_pct = trade.get('pnl_pct', 0)
            
            print(f"{str(entry_time):<20} {str(exit_time):<20} {size:<10.4f} ${pnl:<9.2f} {pnl_pct:<9.2f}%")

if __name__ == '__main__':
    run_cli()