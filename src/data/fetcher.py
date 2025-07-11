try:
    import yfinance as yf
except ImportError:
    yf = None

try:
    import ccxt
except ImportError:
    ccxt = None

try:
    import pandas as pd
except ImportError:
    pd = None

from datetime import datetime, timedelta
from typing import Optional, Dict, List
import time

class DataFetcher:
    def __init__(self, data_source: str = 'yfinance'):
        self.data_source = data_source
        
        if data_source == 'binance':
            if ccxt is None:
                raise ImportError("ccxt not installed. Install with: pip install ccxt")
            self.exchange = ccxt.binance({
                'apiKey': '',
                'secret': '',
                'sandbox': False,
                'enableRateLimit': True,
            })
    
    def fetch_data(self, symbol: str, interval: str, start_date: str, end_date: str):
        """
        Fetch OHLCV data for a single timeframe
        """
        if self.data_source == 'yfinance':
            return self._fetch_yfinance_data(symbol, interval, start_date, end_date)
        elif self.data_source == 'binance':
            return self._fetch_binance_data(symbol, interval, start_date, end_date)
        else:
            raise ValueError(f"Unsupported data source: {self.data_source}")
    
    def fetch_multiple_timeframes(self, symbol: str, timeframes: List[str], 
                                  start_date: str, end_date: str):
        """
        Fetch OHLCV data for multiple timeframes
        
        Args:
            symbol: Trading symbol
            timeframes: List of timeframe strings ['1h', '4h', '1d']
            start_date: Start date string
            end_date: End date string
            
        Returns:
            Dictionary with timeframe as key and DataFrame as value
        """
        data = {}
        
        for timeframe in timeframes:
            try:
                df = self.fetch_data(symbol, timeframe, start_date, end_date)
                if df is not None and not df.empty:
                    data[timeframe] = df
                    # Small delay to avoid rate limits
                    time.sleep(0.1)
            except Exception as e:
                print(f"Error fetching {timeframe} data: {e}")
                continue
        
        return data
    
    def _fetch_yfinance_data(self, symbol: str, interval: str, start_date: str, end_date: str):
        """Fetch data from Yahoo Finance"""
        if yf is None:
            raise ImportError("yfinance not installed. Install with: pip install yfinance")
        if pd is None:
            raise ImportError("pandas not installed. Install with: pip install pandas")
            
        try:
            # Convert interval to yfinance format
            yf_interval = self._convert_interval_yfinance(interval)
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date, interval=yf_interval)
            
            if df.empty:
                print(f"No data available for {symbol}")
                return None
            
            # Standardize column names
            df.columns = df.columns.str.lower()
            df = df.rename(columns={'adj close': 'adj_close'})
            
            # Ensure we have required columns
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in required_columns:
                if col not in df.columns:
                    print(f"Missing required column: {col}")
                    return None
            
            # Remove timezone info and ensure datetime index
            if df.index.tz is not None:
                df.index = df.index.tz_localize(None)
            
            return df[required_columns]
        
        except Exception as e:
            print(f"Error fetching data from Yahoo Finance: {e}")
            return None
    
    def _fetch_binance_data(self, symbol: str, interval: str, start_date: str, end_date: str):
        """Fetch data from Binance"""
        try:
            # Convert dates to timestamps
            start_ts = int(pd.Timestamp(start_date).timestamp() * 1000)
            end_ts = int(pd.Timestamp(end_date).timestamp() * 1000)
            
            # Convert symbol format for Binance
            if '-' in symbol:
                symbol = symbol.replace('-', '')
            
            # Fetch OHLCV data
            ohlcv = self.exchange.fetch_ohlcv(
                symbol, 
                interval, 
                since=start_ts,
                limit=1000
            )
            
            if not ohlcv:
                print(f"No data available for {symbol}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Filter by date range
            df = df[(df.index >= start_date) & (df.index <= end_date)]
            
            return df
        
        except Exception as e:
            print(f"Error fetching data from Binance: {e}")
            return None
    
    def _convert_interval_yfinance(self, interval: str) -> str:
        """Convert standard interval to yfinance format"""
        interval_map = {
            '1m': '1m',
            '2m': '2m',
            '5m': '5m',
            '15m': '15m',
            '30m': '30m',
            '60m': '1h',
            '90m': '90m',
            '1h': '1h',
            '1d': '1d',
            '5d': '5d',
            '1wk': '1wk',
            '1mo': '1mo',
            '3mo': '3mo',
            # Additional mappings
            '4h': '1h',  # Will need to resample
            '2h': '1h',  # Will need to resample
            '6h': '1h',  # Will need to resample
            '8h': '1h',  # Will need to resample
            '12h': '1h', # Will need to resample
        }
        
        base_interval = interval_map.get(interval, interval)
        
        # For intervals not directly supported, fetch hourly and resample
        if interval in ['2h', '4h', '6h', '8h', '12h']:
            return '1h'
        
        return base_interval
    
    def resample_data(self, df, target_interval: str):
        """
        Resample data to a different timeframe
        
        Args:
            df: DataFrame with OHLCV data
            target_interval: Target interval (e.g., '4h', '2h')
            
        Returns:
            Resampled DataFrame
        """
        if pd is None:
            raise ImportError("pandas not installed. Install with: pip install pandas")
            
        try:
            # Define resampling rules
            agg_dict = {
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }
            
            # Convert interval to pandas frequency
            freq_map = {
                '2h': '2H',
                '4h': '4H',
                '6h': '6H',
                '8h': '8H',
                '12h': '12H',
                '2d': '2D',
                '3d': '3D',
                '1w': 'W',
                '1W': 'W'
            }
            
            freq = freq_map.get(target_interval, target_interval)
            
            # Resample the data
            resampled = df.resample(freq).agg(agg_dict)
            
            # Remove rows with NaN values
            resampled = resampled.dropna()
            
            return resampled
        
        except Exception as e:
            print(f"Error resampling data: {e}")
            return df
    
    def get_latest_price(self, symbol: str):
        """Get latest price for a symbol"""
        try:
            if self.data_source == 'yfinance':
                ticker = yf.Ticker(symbol)
                data = ticker.history(period='1d', interval='1m')
                if not data.empty:
                    return float(data['Close'].iloc[-1])
            elif self.data_source == 'binance':
                ticker = self.exchange.fetch_ticker(symbol.replace('-', ''))
                return float(ticker['last'])
            
            return None
        except Exception as e:
            print(f"Error getting latest price: {e}")
            return None
    
    def validate_symbol(self, symbol: str) -> bool:
        """Validate if symbol exists"""
        try:
            if self.data_source == 'yfinance':
                ticker = yf.Ticker(symbol)
                data = ticker.history(period='1d')
                return not data.empty
            elif self.data_source == 'binance':
                markets = self.exchange.load_markets()
                return symbol.replace('-', '') in markets
            
            return False
        except Exception as e:
            print(f"Error validating symbol: {e}")
            return False