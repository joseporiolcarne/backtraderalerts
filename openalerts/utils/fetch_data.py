import pandas as pd
import ccxt
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional


def fetch_crypto_data(symbol: str, timeframe: str = '1h', limit: int = 100, exchange: str = 'binance') -> pd.DataFrame:
    """Fetch cryptocurrency data using ccxt"""
    try:
        exchange_class = getattr(ccxt, exchange)
        exchange_obj = exchange_class({'enableRateLimit': True})
        
        # Convert timeframe to ccxt format
        timeframe_map = {
            '1h': '1h',
            '4h': '4h',
            '1d': '1d',
            '1w': '1w'
        }
        
        tf = timeframe_map.get(timeframe, '1h')
        
        # Fetch OHLCV data
        ohlcv = exchange_obj.fetch_ohlcv(symbol, tf, limit=limit)
        
        # Convert to DataFrame
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('datetime', inplace=True)
        df.drop('timestamp', axis=1, inplace=True)
        
        return df
        
    except Exception as e:
        print(f"Error fetching crypto data: {e}")
        return pd.DataFrame()


def fetch_stock_data(symbol: str, timeframe: str = '1h', limit: int = 100) -> pd.DataFrame:
    """Fetch stock data using yfinance"""
    try:
        # Calculate period based on timeframe and limit
        period_map = {
            '1h': f'{limit}h',
            '4h': f'{limit*4}h',
            '1d': f'{limit}d',
            '1w': f'{limit}wk'
        }
        
        # Interval mapping for yfinance
        interval_map = {
            '1h': '1h',
            '4h': '1h',  # yfinance doesn't have 4h, we'll resample
            '1d': '1d',
            '1w': '1wk'
        }
        
        ticker = yf.Ticker(symbol)
        
        # Calculate start date
        if timeframe == '1h':
            start = datetime.now() - timedelta(hours=limit)
        elif timeframe == '4h':
            start = datetime.now() - timedelta(hours=limit*4)
        elif timeframe == '1d':
            start = datetime.now() - timedelta(days=limit)
        else:  # 1w
            start = datetime.now() - timedelta(weeks=limit)
        
        # Fetch data
        df = ticker.history(start=start, interval=interval_map[timeframe])
        
        # Resample if needed (for 4h)
        if timeframe == '4h':
            df = df.resample('4H').agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            })
        
        # Rename columns to lowercase
        df.columns = df.columns.str.lower()
        
        # Ensure we have datetime index
        if df.index.name != 'datetime':
            df.index.name = 'datetime'
        
        return df.dropna()
        
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return pd.DataFrame()


def fetch_data(symbol: str, timeframe: str = '1h', limit: int = 100, asset_type: Optional[str] = None) -> pd.DataFrame:
    """
    Unified data fetcher for both crypto and stocks
    
    Args:
        symbol: Trading symbol (e.g., 'BTC/USDT' for crypto, 'AAPL' for stocks)
        timeframe: Time interval ('1h', '4h', '1d', '1w')
        limit: Number of bars to fetch
        asset_type: 'crypto' or 'stock' (auto-detected if not provided)
    
    Returns:
        DataFrame with columns: ['open', 'high', 'low', 'close', 'volume']
    """
    
    # Auto-detect asset type if not provided
    if asset_type is None:
        if '/' in symbol or symbol.upper() in ['BTCUSDT', 'ETHUSDT']:
            asset_type = 'crypto'
        else:
            asset_type = 'stock'
    
    if asset_type == 'crypto':
        return fetch_crypto_data(symbol, timeframe, limit)
    else:
        return fetch_stock_data(symbol, timeframe, limit)