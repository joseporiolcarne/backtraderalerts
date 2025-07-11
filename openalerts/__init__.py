# Make imports available at package level
from .strategies.rsi_crossover import RSICrossover, MultiIndicatorAlert
from .engine.runner import run_strategy, run_live_monitoring, backtest_strategy
from .alerts.telegram import TelegramDispatcher, send_telegram
from .utils.fetch_data import fetch_data, fetch_crypto_data, fetch_stock_data

__version__ = "1.0.0"
__all__ = [
    'RSICrossover',
    'MultiIndicatorAlert', 
    'run_strategy',
    'run_live_monitoring',
    'backtest_strategy',
    'TelegramDispatcher',
    'send_telegram',
    'fetch_data',
    'fetch_crypto_data',
    'fetch_stock_data'
]