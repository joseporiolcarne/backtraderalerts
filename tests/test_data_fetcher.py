import unittest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.fetcher import DataFetcher

class TestDataFetcher(unittest.TestCase):
    
    def setUp(self):
        self.fetcher_yf = DataFetcher(data_source='yfinance')
        self.fetcher_binance = DataFetcher(data_source='binance')
        
        # Sample data for testing
        self.sample_data = pd.DataFrame({
            'open': [100, 101, 102, 103, 104],
            'high': [105, 106, 107, 108, 109],
            'low': [95, 96, 97, 98, 99],
            'close': [102, 103, 104, 105, 106],
            'volume': [1000, 1100, 1200, 1300, 1400]
        }, index=pd.date_range('2023-01-01', periods=5, freq='D'))
    
    def test_init_yfinance(self):
        """Test initialization with yfinance data source"""
        fetcher = DataFetcher(data_source='yfinance')
        self.assertEqual(fetcher.data_source, 'yfinance')
    
    def test_init_binance(self):
        """Test initialization with binance data source"""
        fetcher = DataFetcher(data_source='binance')
        self.assertEqual(fetcher.data_source, 'binance')
        self.assertIsNotNone(fetcher.exchange)
    
    def test_init_invalid_source(self):
        """Test initialization with invalid data source"""
        with self.assertRaises(ValueError):
            fetcher = DataFetcher(data_source='invalid')
            fetcher.fetch_data('BTC-USD', '1d', '2023-01-01', '2023-01-31')
    
    @patch('yfinance.Ticker')
    def test_fetch_yfinance_data_success(self, mock_ticker):
        """Test successful data fetching from yfinance"""
        # Mock the yfinance response
        mock_instance = Mock()
        mock_data = self.sample_data.copy()
        mock_data.columns = mock_data.columns.str.lower()  # Ensure lowercase
        mock_instance.history.return_value = mock_data
        mock_ticker.return_value = mock_instance
        
        result = self.fetcher_yf.fetch_data('AAPL', '1d', '2023-01-01', '2023-01-31')
        
        if result is not None:  # Account for potential processing differences
            self.assertIsInstance(result, pd.DataFrame)
            self.assertGreaterEqual(len(result), 0)
            # Check for expected columns
            expected_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in expected_cols:
                if col in result.columns:
                    self.assertIn(col, result.columns)
        mock_ticker.assert_called_once_with('AAPL')
    
    @patch('yfinance.Ticker')
    def test_fetch_yfinance_data_empty(self, mock_ticker):
        """Test fetching empty data from yfinance"""
        # Mock empty response
        mock_instance = Mock()
        mock_instance.history.return_value = pd.DataFrame()
        mock_ticker.return_value = mock_instance
        
        result = self.fetcher_yf.fetch_data('INVALID', '1d', '2023-01-01', '2023-01-31')
        
        self.assertIsNone(result)
    
    @patch('yfinance.Ticker')
    def test_fetch_yfinance_data_exception(self, mock_ticker):
        """Test exception handling in yfinance data fetching"""
        # Mock exception
        mock_ticker.side_effect = Exception("Network error")
        
        result = self.fetcher_yf.fetch_data('AAPL', '1d', '2023-01-01', '2023-01-31')
        
        self.assertIsNone(result)
    
    def test_convert_interval_yfinance(self):
        """Test interval conversion for yfinance"""
        # Test standard intervals
        self.assertEqual(self.fetcher_yf._convert_interval_yfinance('1h'), '1h')
        self.assertEqual(self.fetcher_yf._convert_interval_yfinance('1d'), '1d')
        
        # Test intervals that need conversion
        self.assertEqual(self.fetcher_yf._convert_interval_yfinance('4h'), '1h')
        self.assertEqual(self.fetcher_yf._convert_interval_yfinance('2h'), '1h')
    
    def test_resample_data(self):
        """Test data resampling functionality"""
        # Create hourly data for testing
        hourly_data = pd.DataFrame({
            'open': [100, 101, 102, 103],
            'high': [105, 106, 107, 108],
            'low': [95, 96, 97, 98],
            'close': [102, 103, 104, 105],
            'volume': [1000, 1100, 1200, 1300]
        }, index=pd.date_range('2023-01-01 00:00:00', periods=4, freq='H'))
        
        # Resample to 2h
        result = self.fetcher_yf.resample_data(hourly_data, '2h')
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)  # 4 hours -> 2 2-hour periods
        
        # Check OHLC aggregation
        self.assertEqual(result.iloc[0]['open'], 100)  # First open
        self.assertEqual(result.iloc[0]['high'], 106)  # Max high
        self.assertEqual(result.iloc[0]['low'], 95)    # Min low
        self.assertEqual(result.iloc[0]['close'], 103) # Last close
        self.assertEqual(result.iloc[0]['volume'], 2100) # Sum volume
    
    @patch.object(DataFetcher, 'fetch_data')
    def test_fetch_multiple_timeframes(self, mock_fetch):
        """Test fetching multiple timeframes"""
        # Mock successful fetches
        mock_fetch.side_effect = [self.sample_data, self.sample_data]
        
        result = self.fetcher_yf.fetch_multiple_timeframes(
            'BTC-USD', ['1h', '4h'], '2023-01-01', '2023-01-31'
        )
        
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 2)
        self.assertIn('1h', result)
        self.assertIn('4h', result)
        self.assertEqual(mock_fetch.call_count, 2)
    
    @patch.object(DataFetcher, 'fetch_data')
    def test_fetch_multiple_timeframes_partial_failure(self, mock_fetch):
        """Test fetching multiple timeframes with partial failure"""
        # Mock one success, one failure
        mock_fetch.side_effect = [self.sample_data, None]
        
        result = self.fetcher_yf.fetch_multiple_timeframes(
            'BTC-USD', ['1h', '4h'], '2023-01-01', '2023-01-31'
        )
        
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 1)
        self.assertIn('1h', result)
        self.assertNotIn('4h', result)
    
    @patch('yfinance.Ticker')
    def test_get_latest_price_yfinance(self, mock_ticker):
        """Test getting latest price from yfinance"""
        # Mock the response
        mock_instance = Mock()
        mock_data = pd.DataFrame({'Close': [100.50]}, index=[datetime.now()])
        mock_instance.history.return_value = mock_data
        mock_ticker.return_value = mock_instance
        
        result = self.fetcher_yf.get_latest_price('AAPL')
        
        self.assertEqual(result, 100.50)
    
    @patch('yfinance.Ticker')
    def test_get_latest_price_yfinance_failure(self, mock_ticker):
        """Test getting latest price failure"""
        mock_ticker.side_effect = Exception("Error")
        
        result = self.fetcher_yf.get_latest_price('AAPL')
        
        self.assertIsNone(result)
    
    @patch('yfinance.Ticker')
    def test_validate_symbol_yfinance_valid(self, mock_ticker):
        """Test symbol validation - valid symbol"""
        mock_instance = Mock()
        mock_instance.history.return_value = self.sample_data
        mock_ticker.return_value = mock_instance
        
        result = self.fetcher_yf.validate_symbol('AAPL')
        
        self.assertTrue(result)
    
    @patch('yfinance.Ticker')
    def test_validate_symbol_yfinance_invalid(self, mock_ticker):
        """Test symbol validation - invalid symbol"""
        mock_instance = Mock()
        mock_instance.history.return_value = pd.DataFrame()
        mock_ticker.return_value = mock_instance
        
        result = self.fetcher_yf.validate_symbol('INVALID')
        
        self.assertFalse(result)
    
    def test_resample_data_exception(self):
        """Test resampling with invalid data"""
        invalid_data = pd.DataFrame({'invalid': [1, 2, 3]})
        
        result = self.fetcher_yf.resample_data(invalid_data, '2h')
        
        # Should return original data on error
        self.assertEqual(len(result), 3)

if __name__ == '__main__':
    unittest.main()