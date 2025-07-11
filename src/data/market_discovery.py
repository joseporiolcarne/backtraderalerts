"""
Market Discovery Module
Provides functionality to discover and list available markets from different data sources
"""
import sys
import os
from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta
import json
import logging

# Try to import pandas
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

# Set up logging
logger = logging.getLogger(__name__)

# Try to import data source libraries
try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False
    logger.warning("ccxt not available - crypto markets will be limited")

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    logger.warning("yfinance not available - stock markets will be limited")

class MarketDiscovery:
    """
    Discovers and manages available markets from various data sources
    """
    
    def __init__(self, data_source: str = 'auto'):
        """
        Initialize market discovery for a specific data source
        
        Args:
            data_source: Data source to use ('yfinance', 'ccxt', 'auto', exchange_name)
        """
        self.data_source = data_source
        self.cache_file = f"cache/markets_{data_source}.json"
        self.cache_duration = 24 * 60 * 60  # 24 hours in seconds
        self._market_cache = None
        self._exchange = None
        
        # Ensure cache directory exists
        os.makedirs('cache', exist_ok=True)
        
        # Initialize CCXT exchange if needed
        if data_source != 'yfinance' and CCXT_AVAILABLE:
            self._init_ccxt_exchange(data_source)
    
    def _init_ccxt_exchange(self, exchange_name: str):
        """Initialize CCXT exchange"""
        try:
            if exchange_name == 'auto' or exchange_name == 'ccxt':
                # Default to binance for crypto
                self._exchange = ccxt.binance()
            elif hasattr(ccxt, exchange_name):
                exchange_class = getattr(ccxt, exchange_name)
                self._exchange = exchange_class()
            else:
                logger.warning(f"Exchange {exchange_name} not found in ccxt")
        except Exception as e:
            logger.error(f"Failed to initialize CCXT exchange: {e}")
    
    def get_popular_markets(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Get a curated list of popular markets by category
        
        Returns:
            Dict with categories and their popular markets
        """
        popular_markets = {}
        
        # Get crypto markets from CCXT if available
        if CCXT_AVAILABLE and self._exchange:
            try:
                popular_markets["Cryptocurrencies"] = self._get_ccxt_crypto_markets()
            except Exception as e:
                logger.error(f"Failed to get CCXT markets: {e}")
                popular_markets["Cryptocurrencies"] = self._get_fallback_crypto_markets()
        else:
            popular_markets["Cryptocurrencies"] = self._get_fallback_crypto_markets()
        
        # Get stock markets from yfinance if available
        if YFINANCE_AVAILABLE:
            popular_markets.update(self._get_yfinance_markets())
        else:
            popular_markets.update(self._get_fallback_stock_markets())
        
        return popular_markets
    
    def _get_ccxt_crypto_markets(self) -> List[Dict[str, str]]:
        """Get cryptocurrency markets from CCXT"""
        markets = []
        
        try:
            # Load markets from exchange
            self._exchange.load_markets()
            
            # Get popular trading pairs
            popular_symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 
                             'SOL/USDT', 'MATIC/USDT', 'AVAX/USDT', 'DOT/USDT',
                             'LINK/USDT', 'XRP/USDT', 'DOGE/USDT', 'LTC/USDT']
            
            for symbol in popular_symbols:
                if symbol in self._exchange.markets:
                    market_info = self._exchange.markets[symbol]
                    base = market_info['base']
                    quote = market_info['quote']
                    
                    # Try to get ticker for current price
                    try:
                        ticker = self._exchange.fetch_ticker(symbol)
                        price = ticker.get('last', 0)
                        change = ticker.get('percentage', 0)
                    except:
                        price = 0
                        change = 0
                    
                    markets.append({
                        "symbol": symbol.replace('/', '-'),
                        "name": f"{base} / {quote}",
                        "exchange": self._exchange.name,
                        "price": float(price) if price is not None else 0,
                        "change_24h": float(change) if change is not None else 0,
                        "base": base,
                        "quote": quote
                    })
            
            return markets[:10]  # Return top 10
            
        except Exception as e:
            logger.error(f"Error fetching CCXT markets: {e}")
            return self._get_fallback_crypto_markets()
    
    def _get_yfinance_markets(self) -> Dict[str, List[Dict[str, str]]]:
        """Get stock markets from yfinance using bulk download"""
        markets = {}
        
        # Popular US stocks
        us_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'AMD', 'INTC']
        
        try:
            # Use yfinance bulk download for efficiency
            stock_data = yf.download(us_stocks, period='2d', group_by='ticker', progress=False)
            tickers = yf.Tickers(' '.join(us_stocks))
            
            stock_list = []
            for symbol in us_stocks:
                try:
                    # Get detailed info
                    ticker_info = tickers.tickers[symbol].info
                    
                    # Get price data from bulk download
                    if symbol in stock_data.columns.levels[0]:
                        ticker_data = stock_data[symbol]
                        if not ticker_data.empty and len(ticker_data) >= 2:
                            current_price = ticker_data['Close'].iloc[-1]
                            prev_close = ticker_data['Close'].iloc[-2]
                            change = ((current_price - prev_close) / prev_close) * 100
                            volume = ticker_data['Volume'].iloc[-1]
                        else:
                            current_price = ticker_info.get('regularMarketPrice', 0)
                            change = ticker_info.get('regularMarketChangePercent', 0)
                            volume = ticker_info.get('regularMarketVolume', 0)
                    else:
                        current_price = ticker_info.get('regularMarketPrice', 0)
                        change = ticker_info.get('regularMarketChangePercent', 0)
                        volume = ticker_info.get('regularMarketVolume', 0)
                    
                    stock_list.append({
                        "symbol": symbol,
                        "name": ticker_info.get('longName', symbol),
                        "exchange": ticker_info.get('exchange', 'NASDAQ'),
                        "price": float(current_price) if current_price is not None else 0,
                        "change_24h": float(change) if change is not None else 0,
                        "volume": int(volume) if volume is not None else 0,
                        "sector": ticker_info.get('sector', 'Technology'),
                        "market_cap": ticker_info.get('marketCap', 0),
                        "pe_ratio": ticker_info.get('trailingPE', 0),
                        "dividend_yield": ticker_info.get('dividendYield', 0)
                    })
                except Exception as e:
                    logger.warning(f"Failed to get info for {symbol}: {e}")
                    # Add with basic info
                    stock_list.append({
                        "symbol": symbol,
                        "name": symbol,
                        "exchange": "NASDAQ",
                        "price": 0,
                        "change_24h": 0,
                        "volume": 0
                    })
            
        except Exception as e:
            logger.error(f"Failed bulk download: {e}")
            # Fallback to individual ticker approach
            stock_list = []
            for symbol in us_stocks:
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    hist = ticker.history(period="2d")
                    
                    if not hist.empty and len(hist) >= 2:
                        current_price = hist['Close'].iloc[-1]
                        prev_close = hist['Close'].iloc[-2]
                        change = ((current_price - prev_close) / prev_close) * 100
                        volume = hist['Volume'].iloc[-1]
                    else:
                        current_price = info.get('regularMarketPrice', 0)
                        change = info.get('regularMarketChangePercent', 0)
                        volume = info.get('regularMarketVolume', 0)
                    
                    stock_list.append({
                        "symbol": symbol,
                        "name": info.get('longName', symbol),
                        "exchange": info.get('exchange', 'NASDAQ'),
                        "price": float(current_price) if current_price is not None else 0,
                        "change_24h": float(change) if change is not None else 0,
                        "volume": int(volume) if volume is not None else 0,
                        "sector": info.get('sector', 'Technology'),
                        "market_cap": info.get('marketCap', 0)
                    })
                except Exception as e:
                    logger.warning(f"Failed to get info for {symbol}: {e}")
                    stock_list.append({
                        "symbol": symbol,
                        "name": symbol,
                        "exchange": "NASDAQ",
                        "price": 0,
                        "change_24h": 0,
                        "volume": 0
                    })
        
        markets["US Stocks"] = stock_list
        
        # Forex pairs
        forex_pairs = ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'USDCHF=X', 'AUDUSD=X', 'USDCAD=X']
        forex_list = []
        
        for symbol in forex_pairs:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")
                
                if not hist.empty and len(hist) >= 2:
                    current_price = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2]
                    change = ((current_price - prev_close) / prev_close) * 100
                else:
                    current_price = 0
                    change = 0
                
                # Parse currency pair
                pair_name = symbol.replace('=X', '')
                base = pair_name[:3]
                quote = pair_name[3:]
                
                forex_list.append({
                    "symbol": symbol,
                    "name": f"{base}/{quote}",
                    "exchange": "Forex",
                    "price": current_price,
                    "change_24h": change
                })
            except:
                pass
        
        if forex_list:
            markets["Forex"] = forex_list
        
        # Commodities
        commodities = {
            'GC=F': 'Gold Futures',
            'SI=F': 'Silver Futures',
            'CL=F': 'Crude Oil Futures',
            'NG=F': 'Natural Gas Futures'
        }
        
        commodity_list = []
        for symbol, name in commodities.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")
                
                if not hist.empty and len(hist) >= 2:
                    current_price = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2]
                    change = ((current_price - prev_close) / prev_close) * 100
                else:
                    current_price = 0
                    change = 0
                
                commodity_list.append({
                    "symbol": symbol,
                    "name": name,
                    "exchange": "COMEX/NYMEX",
                    "price": current_price,
                    "change_24h": change
                })
            except:
                pass
        
        if commodity_list:
            markets["Commodities"] = commodity_list
        
        # Indices
        indices = {
            '^GSPC': 'S&P 500',
            '^DJI': 'Dow Jones',
            '^IXIC': 'NASDAQ',
            '^VIX': 'VIX Volatility'
        }
        
        index_list = []
        for symbol, name in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")
                
                if not hist.empty and len(hist) >= 2:
                    current_price = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2]
                    change = ((current_price - prev_close) / prev_close) * 100
                else:
                    current_price = 0
                    change = 0
                
                index_list.append({
                    "symbol": symbol,
                    "name": name,
                    "exchange": "Index",
                    "price": current_price,
                    "change_24h": change
                })
            except:
                pass
        
        if index_list:
            markets["Indices"] = index_list
        
        return markets
    
    def _get_fallback_crypto_markets(self) -> List[Dict[str, str]]:
        """Fallback crypto markets when CCXT is not available"""
        import random
        random.seed(42)  # For consistent demo data
        
        markets = [
            {"symbol": "BTC-USD", "name": "Bitcoin USD", "base_price": 45000},
            {"symbol": "ETH-USD", "name": "Ethereum USD", "base_price": 2500},
            {"symbol": "BNB-USD", "name": "Binance Coin USD", "base_price": 350},
            {"symbol": "ADA-USD", "name": "Cardano USD", "base_price": 0.5},
            {"symbol": "SOL-USD", "name": "Solana USD", "base_price": 120},
        ]
        
        # Add demo prices with some variation
        result = []
        for market in markets:
            base = market['base_price']
            variation = random.uniform(-0.05, 0.05)  # +/- 5%
            price = base * (1 + variation)
            change = random.uniform(-5, 5)
            
            result.append({
                "symbol": market["symbol"],
                "name": market["name"],
                "exchange": "Demo",
                "price": round(price, 2 if price > 10 else 4),
                "change_24h": round(change, 2),
                "volume": random.randint(100000, 10000000)
            })
        
        return result
    
    def _get_fallback_stock_markets(self) -> Dict[str, List[Dict[str, str]]]:
        """Fallback stock markets when yfinance is not available"""
        import random
        random.seed(42)
        
        # Demo data with realistic prices
        demo_data = {
            "US Stocks": [
                ("AAPL", "Apple Inc.", 180),
                ("MSFT", "Microsoft Corporation", 420),
                ("GOOGL", "Alphabet Inc.", 150),
                ("AMZN", "Amazon.com Inc.", 175),
                ("TSLA", "Tesla Inc.", 250),
            ],
            "Forex": [
                ("EURUSD=X", "EUR/USD", 1.08),
                ("GBPUSD=X", "GBP/USD", 1.27),
                ("USDJPY=X", "USD/JPY", 150.5),
            ],
            "Commodities": [
                ("GC=F", "Gold Futures", 2050),
                ("CL=F", "Crude Oil Futures", 78.5),
            ],
            "Indices": [
                ("^GSPC", "S&P 500", 4700),
                ("^DJI", "Dow Jones", 38000),
            ]
        }
        
        result = {}
        for category, items in demo_data.items():
            markets = []
            for symbol, name, base_price in items:
                variation = random.uniform(-0.03, 0.03)
                price = base_price * (1 + variation)
                change = random.uniform(-3, 3)
                
                markets.append({
                    "symbol": symbol,
                    "name": name,
                    "exchange": "Demo",
                    "price": round(price, 2),
                    "change_24h": round(change, 2),
                    "volume": random.randint(1000000, 100000000)
                })
            
            result[category] = markets
        
        return result
    
    def search_markets(self, query: str, limit: int = 50) -> List[Dict[str, str]]:
        """
        Search for markets matching a query
        
        Args:
            query: Search term (symbol, company name, etc.)
            limit: Maximum number of results to return
            
        Returns:
            List of matching markets
        """
        query = query.upper().strip()
        if not query:
            return []
        
        results = []
        
        # Search in CCXT if available
        if CCXT_AVAILABLE and self._exchange:
            results.extend(self._search_ccxt_markets(query, limit))
        
        # Search in yfinance if available
        if YFINANCE_AVAILABLE:
            results.extend(self._search_yfinance_markets(query, limit))
        
        # If no real data available, search through fallback markets
        if not results:
            popular_markets = self.get_popular_markets()
            for category, markets in popular_markets.items():
                for market in markets:
                    if (query in market['symbol'].upper() or 
                        query in market['name'].upper()):
                        market_copy = market.copy()
                        market_copy['category'] = category
                        results.append(market_copy)
        
        # Remove duplicates and limit results
        seen = set()
        unique_results = []
        for market in results:
            if market['symbol'] not in seen:
                seen.add(market['symbol'])
                unique_results.append(market)
                if len(unique_results) >= limit:
                    break
        
        return unique_results
    
    def _search_ccxt_markets(self, query: str, limit: int) -> List[Dict[str, str]]:
        """Search CCXT markets"""
        results = []
        
        try:
            if not self._exchange.markets:
                self._exchange.load_markets()
            
            for symbol, market in self._exchange.markets.items():
                if (query in symbol.upper() or 
                    query in market.get('base', '').upper() or
                    query in market.get('quote', '').upper()):
                    
                    results.append({
                        "symbol": symbol.replace('/', '-'),
                        "name": f"{market['base']} / {market['quote']}",
                        "exchange": self._exchange.name,
                        "category": "Cryptocurrencies",
                        "base": market['base'],
                        "quote": market['quote']
                    })
                    
                    if len(results) >= limit:
                        break
        except Exception as e:
            logger.error(f"CCXT search error: {e}")
        
        return results
    
    def _search_yfinance_markets(self, query: str, limit: int) -> List[Dict[str, str]]:
        """
        Search for markets using yfinance
        
        Args:
            query: Search term
            limit: Maximum results
            
        Returns:
            List of market suggestions
        """
        results = []
        
        # Try direct symbol lookup
        if len(query) <= 6:
            try:
                ticker = yf.Ticker(query)
                info = ticker.info
                
                if info and 'symbol' in info:
                    results.append({
                        "symbol": info.get('symbol', query),
                        "name": info.get('longName', info.get('shortName', query)),
                        "exchange": info.get('exchange', 'Unknown'),
                        "category": "US Stocks" if info.get('quoteType') == 'EQUITY' else "Search Result",
                        "price": info.get('regularMarketPrice', 0),
                        "change_24h": info.get('regularMarketChangePercent', 0)
                    })
            except:
                pass
        
        # Try with common suffixes
        suffixes = ['', '-USD', '=X', '=F']
        for suffix in suffixes:
            test_symbol = query + suffix
            try:
                ticker = yf.Ticker(test_symbol)
                hist = ticker.history(period="1d")
                
                if not hist.empty:
                    # Determine category based on suffix
                    if suffix == '-USD':
                        category = "Cryptocurrencies"
                    elif suffix == '=X':
                        category = "Forex"
                    elif suffix == '=F':
                        category = "Commodities"
                    else:
                        category = "US Stocks"
                    
                    results.append({
                        "symbol": test_symbol,
                        "name": f"{test_symbol}",
                        "exchange": "Market",
                        "category": category,
                        "price": hist['Close'].iloc[-1] if len(hist) > 0 else 0,
                        "change_24h": 0
                    })
            except:
                pass
        
        return results[:limit]
    
    def get_detailed_market_info(self, symbol: str) -> Optional[Dict]:
        """
        Get comprehensive market information using yfinance advanced features
        
        Args:
            symbol: Market symbol to look up
            
        Returns:
            Detailed market information or None if not found
        """
        if not YFINANCE_AVAILABLE:
            return self.get_market_info(symbol)
        
        try:
            ticker = yf.Ticker(symbol)
            
            # Get all available data
            info = ticker.info
            calendar = None
            analyst_targets = None
            financials = None
            
            try:
                calendar = ticker.calendar
            except:
                pass
                
            try:
                analyst_targets = ticker.analyst_price_targets
            except:
                pass
                
            try:
                # Get quarterly financials if available
                financials = ticker.quarterly_income_stmt
            except:
                pass
            
            # Get historical data for price analysis
            hist_1mo = ticker.history(period='1mo')
            hist_1y = ticker.history(period='1y')
            
            # Calculate additional metrics
            price_52w_high = hist_1y['High'].max() if not hist_1y.empty else 0
            price_52w_low = hist_1y['Low'].min() if not hist_1y.empty else 0
            avg_volume_30d = hist_1mo['Volume'].mean() if not hist_1mo.empty else 0
            
            # Build comprehensive info
            detailed_info = {
                # Basic info
                "symbol": symbol,
                "name": info.get('longName', info.get('shortName', symbol)),
                "exchange": info.get('exchange', 'Unknown'),
                "sector": info.get('sector', ''),
                "industry": info.get('industry', ''),
                
                # Price data
                "current_price": info.get('regularMarketPrice', 0),
                "previous_close": info.get('previousClose', 0),
                "open": info.get('open', 0),
                "day_low": info.get('dayLow', 0),
                "day_high": info.get('dayHigh', 0),
                "52_week_low": price_52w_low,
                "52_week_high": price_52w_high,
                
                # Market metrics
                "market_cap": info.get('marketCap', 0),
                "enterprise_value": info.get('enterpriseValue', 0),
                "pe_ratio": info.get('trailingPE', 0),
                "forward_pe": info.get('forwardPE', 0),
                "price_to_book": info.get('priceToBook', 0),
                "profit_margins": info.get('profitMargins', 0),
                
                # Dividend info
                "dividend_yield": info.get('dividendYield', 0),
                "dividend_rate": info.get('dividendRate', 0),
                "ex_dividend_date": info.get('exDividendDate', 0),
                
                # Volume and trading
                "volume": info.get('volume', 0),
                "avg_volume": info.get('averageVolume', 0),
                "avg_volume_30d": int(avg_volume_30d) if avg_volume_30d else 0,
                
                # Analyst data
                "analyst_targets": analyst_targets.to_dict() if analyst_targets is not None and hasattr(analyst_targets, 'to_dict') else {},
                "recommendation": info.get('recommendationKey', ''),
                "target_high_price": info.get('targetHighPrice', 0),
                "target_low_price": info.get('targetLowPrice', 0),
                "target_mean_price": info.get('targetMeanPrice', 0),
                
                # Calendar events
                "earnings_date": calendar.to_dict() if calendar is not None and hasattr(calendar, 'to_dict') else {},
                
                # Company info
                "employees": info.get('fullTimeEmployees', 0),
                "website": info.get('website', ''),
                "business_summary": info.get('longBusinessSummary', ''),
                
                # Risk metrics
                "beta": info.get('beta', 0),
                "trailing_eps": info.get('trailingEps', 0),
                "forward_eps": info.get('forwardEps', 0),
                
                # Financial data
                "total_revenue": info.get('totalRevenue', 0),
                "revenue_growth": info.get('revenueGrowth', 0),
                "gross_margins": info.get('grossMargins', 0),
                "operating_margins": info.get('operatingMargins', 0),
                
                # ETF/Fund specific (if applicable)
                "fund_family": info.get('fundFamily', ''),
                "category": info.get('category', ''),
                "total_assets": info.get('totalAssets', 0),
                
                # Raw data for advanced users
                "raw_info": info,
                "has_financials": financials is not None,
                "data_timestamp": datetime.now().isoformat()
            }
            
            return detailed_info
            
        except Exception as e:
            logger.error(f"Failed to get detailed info for {symbol}: {e}")
            return self.get_market_info(symbol)
    
    def get_market_info(self, symbol: str) -> Optional[Dict[str, str]]:
        """
        Get detailed information about a specific market
        
        Args:
            symbol: Market symbol to look up
            
        Returns:
            Market information or None if not found
        """
        # First check popular markets
        popular_markets = self.get_popular_markets()
        for category, markets in popular_markets.items():
            for market in markets:
                if market['symbol'].upper() == symbol.upper():
                    market_info = market.copy()
                    market_info['category'] = category
                    return market_info
        
        # If not found in popular markets, return basic info
        return {
            "symbol": symbol.upper(),
            "name": f"{symbol.upper()} (Unknown)",
            "exchange": "Unknown",
            "category": "User Defined"
        }
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate if a symbol is likely to be valid
        
        Args:
            symbol: Symbol to validate
            
        Returns:
            True if symbol appears valid
        """
        if not symbol or len(symbol.strip()) == 0:
            return False
        
        symbol = symbol.strip().upper()
        
        # Basic validation rules
        if len(symbol) > 20:  # Too long
            return False
        
        if len(symbol) < 1:  # Too short
            return False
        
        # Check for valid characters (letters, numbers, common separators)
        valid_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-=^.')
        if not all(c in valid_chars for c in symbol):
            return False
        
        return True
    
    def get_market_categories(self) -> List[str]:
        """
        Get list of available market categories
        
        Returns:
            List of category names
        """
        popular_markets = self.get_popular_markets()
        return list(popular_markets.keys())
    
    def get_markets_by_category(self, category: str) -> List[Dict[str, str]]:
        """
        Get all markets in a specific category
        
        Args:
            category: Category name
            
        Returns:
            List of markets in the category
        """
        popular_markets = self.get_popular_markets()
        return popular_markets.get(category, [])
    
    def get_trending_markets(self) -> List[Dict[str, str]]:
        """
        Get a list of trending/most active markets
        
        Returns:
            List of trending markets
        """
        trending = []
        
        # Get trending from CCXT (by volume)
        if CCXT_AVAILABLE and self._exchange:
            try:
                # Get tickers with volume
                tickers = self._exchange.fetch_tickers()
                
                # Sort by volume and get top markets
                sorted_tickers = sorted(
                    [(symbol, data) for symbol, data in tickers.items() if data.get('quoteVolume', 0) > 0],
                    key=lambda x: x[1].get('quoteVolume', 0),
                    reverse=True
                )[:5]  # Top 5 by volume
                
                for symbol, ticker in sorted_tickers:
                    market = self._exchange.markets.get(symbol, {})
                    trending.append({
                        "symbol": symbol.replace('/', '-'),
                        "name": f"{market.get('base', '')} / {market.get('quote', '')}",
                        "exchange": self._exchange.name,
                        "category": "Cryptocurrencies",
                        "price": ticker.get('last', 0),
                        "change_24h": ticker.get('percentage', 0),
                        "volume": ticker.get('quoteVolume', 0)
                    })
            except Exception as e:
                logger.error(f"Failed to get CCXT trending: {e}")
        
        # Get trending stocks from yfinance
        if YFINANCE_AVAILABLE:
            # Most active stocks (you could also use gainers/losers)
            trending_symbols = ['TSLA', 'AAPL', 'NVDA', 'AMD', 'MSFT']  # Common trending stocks
            
            for symbol in trending_symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    hist = ticker.history(period="2d")
                    
                    if not hist.empty and len(hist) >= 2:
                        current_price = hist['Close'].iloc[-1]
                        prev_close = hist['Close'].iloc[-2]
                        change = ((current_price - prev_close) / prev_close) * 100
                        volume = hist['Volume'].iloc[-1]
                    else:
                        current_price = info.get('regularMarketPrice', 0)
                        change = info.get('regularMarketChangePercent', 0)
                        volume = info.get('regularMarketVolume', 0)
                    
                    trending.append({
                        "symbol": symbol,
                        "name": info.get('longName', symbol),
                        "exchange": info.get('exchange', 'NASDAQ'),
                        "category": "US Stocks",
                        "price": current_price,
                        "change_24h": change,
                        "volume": volume
                    })
                except:
                    pass
        
        # If no real data, return fallback
        if not trending:
            trending = [
                {"symbol": "BTC-USD", "name": "Bitcoin USD", "exchange": "Crypto", "category": "Cryptocurrencies"},
                {"symbol": "TSLA", "name": "Tesla Inc.", "exchange": "NASDAQ", "category": "US Stocks"},
                {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ", "category": "US Stocks"},
            ]
        
        return trending
    
    def save_custom_market(self, symbol: str, name: str, exchange: str = "Custom") -> bool:
        """
        Save a custom market to the user's list
        
        Args:
            symbol: Market symbol
            name: Market name
            exchange: Exchange name
            
        Returns:
            True if saved successfully
        """
        if not self.validate_symbol(symbol):
            return False
        
        custom_markets_file = "cache/custom_markets.json"
        custom_markets = []
        
        # Load existing custom markets
        try:
            if os.path.exists(custom_markets_file):
                with open(custom_markets_file, 'r') as f:
                    custom_markets = json.load(f)
        except:
            custom_markets = []
        
        # Add new market (avoid duplicates)
        market = {
            "symbol": symbol.upper(),
            "name": name,
            "exchange": exchange,
            "category": "Custom",
            "added_date": datetime.now().isoformat()
        }
        
        # Remove existing entry if it exists
        custom_markets = [m for m in custom_markets if m['symbol'] != symbol.upper()]
        custom_markets.append(market)
        
        # Save back to file
        try:
            with open(custom_markets_file, 'w') as f:
                json.dump(custom_markets, f, indent=2)
            return True
        except:
            return False
    
    def get_custom_markets(self) -> List[Dict[str, str]]:
        """
        Get user's custom markets
        
        Returns:
            List of custom markets
        """
        custom_markets_file = "cache/custom_markets.json"
        
        try:
            if os.path.exists(custom_markets_file):
                with open(custom_markets_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        
        return []
    
    def get_all_available_markets(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Get all available markets organized by category
        
        Returns:
            Dictionary with all markets by category
        """
        all_markets = self.get_popular_markets()
        
        # Add custom markets if any
        custom_markets = self.get_custom_markets()
        if custom_markets:
            all_markets["Custom"] = custom_markets
        
        return all_markets
    
    def get_available_exchanges(self) -> List[str]:
        """
        Get list of available exchanges from CCXT
        
        Returns:
            List of exchange names
        """
        if CCXT_AVAILABLE:
            return ccxt.exchanges
        return ['binance', 'coinbase', 'kraken', 'bitfinex']  # Fallback list
    
    def switch_exchange(self, exchange_name: str) -> bool:
        """
        Switch to a different CCXT exchange
        
        Args:
            exchange_name: Name of the exchange
            
        Returns:
            True if successful, False otherwise
        """
        if CCXT_AVAILABLE and exchange_name in ccxt.exchanges:
            try:
                self._init_ccxt_exchange(exchange_name)
                return True
            except Exception as e:
                logger.error(f"Failed to switch to {exchange_name}: {e}")
        return False
    
    def download_historical_data(self, symbols: List[str], period: str = '1mo', 
                                interval: str = '1d'):
        """
        Download historical data for multiple symbols using yf.download()
        
        Args:
            symbols: List of symbols to download
            period: Period to download (1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max)
            interval: Data interval (1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo)
            
        Returns:
            DataFrame with historical data
        """
        if not YFINANCE_AVAILABLE:
            logger.error("yfinance not available for historical data download")
            return pd.DataFrame() if PANDAS_AVAILABLE else None
        
        if not PANDAS_AVAILABLE:
            logger.error("pandas not available for data handling")
            return None
        
        try:
            # Use yfinance bulk download
            data = yf.download(
                symbols, 
                period=period, 
                interval=interval,
                group_by='ticker' if len(symbols) > 1 else None,
                progress=False,
                auto_adjust=True,
                prepost=True
            )
            
            logger.info(f"Downloaded {period} data for {len(symbols)} symbols")
            return data
            
        except Exception as e:
            logger.error(f"Failed to download historical data: {e}")
            return pd.DataFrame() if PANDAS_AVAILABLE else None
    
    def get_fund_data(self, symbol: str) -> Optional[Dict]:
        """
        Get ETF/Fund specific data using yfinance
        
        Args:
            symbol: Fund symbol (e.g., 'SPY', 'QQQ')
            
        Returns:
            Fund data including holdings and performance
        """
        if not YFINANCE_AVAILABLE:
            return None
        
        try:
            ticker = yf.Ticker(symbol)
            
            # Check if it has fund data
            try:
                fund_data = ticker.funds_data
                if fund_data is None:
                    return None
                
                fund_info = {
                    "symbol": symbol,
                    "type": "ETF/Fund",
                    "description": getattr(fund_data, 'description', ''),
                    "top_holdings": getattr(fund_data, 'top_holdings', pd.DataFrame() if PANDAS_AVAILABLE else {}).to_dict('records') if hasattr(fund_data, 'top_holdings') and PANDAS_AVAILABLE else [],
                    "sector_weightings": getattr(fund_data, 'sector_weightings', {}),
                    "equity_holdings": getattr(fund_data, 'equity_holdings', {}),
                    "bond_holdings": getattr(fund_data, 'bond_holdings', {}),
                    "basic_info": ticker.info,
                    "data_timestamp": datetime.now().isoformat()
                }
                
                return fund_info
                
            except Exception as e:
                logger.warning(f"No fund data available for {symbol}: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get fund data for {symbol}: {e}")
            return None
    
    def get_options_data(self, symbol: str) -> Optional[Dict]:
        """
        Get options chain data for a symbol
        
        Args:
            symbol: Symbol to get options for
            
        Returns:
            Options chain data
        """
        if not YFINANCE_AVAILABLE:
            return None
        
        try:
            ticker = yf.Ticker(symbol)
            
            # Get available options dates
            options_dates = ticker.options
            if not options_dates:
                return None
            
            # Get options for the nearest expiry
            nearest_expiry = options_dates[0]
            options_chain = ticker.option_chain(nearest_expiry)
            
            options_info = {
                "symbol": symbol,
                "expiry_date": nearest_expiry,
                "calls": options_chain.calls.to_dict('records'),
                "puts": options_chain.puts.to_dict('records'),
                "available_expiries": list(options_dates),
                "data_timestamp": datetime.now().isoformat()
            }
            
            return options_info
            
        except Exception as e:
            logger.warning(f"No options data available for {symbol}: {e}")
            return None
    
    def get_trending_markets(self) -> List[Dict[str, str]]:
        """
        Get a list of trending/most active markets using real yfinance data
        
        Returns:
            List of trending markets
        """
        trending = []
        
        # Get trending from yfinance using multiple approaches
        if YFINANCE_AVAILABLE:
            # Most active large cap stocks
            trending_symbols = ['TSLA', 'AAPL', 'NVDA', 'AMD', 'MSFT', 'AMZN', 'GOOGL', 'META']
            
            try:
                # Use bulk download for efficiency
                trending_data = yf.download(trending_symbols, period='2d', progress=False)
                tickers = yf.Tickers(' '.join(trending_symbols))
                
                for symbol in trending_symbols:
                    try:
                        ticker_info = tickers.tickers[symbol].info
                        
                        # Calculate metrics from historical data
                        if symbol in trending_data.columns.levels[0]:
                            symbol_data = trending_data[symbol]
                            if not symbol_data.empty and len(symbol_data) >= 2:
                                current_price = symbol_data['Close'].iloc[-1]
                                prev_close = symbol_data['Close'].iloc[-2]
                                change = ((current_price - prev_close) / prev_close) * 100
                                volume = symbol_data['Volume'].iloc[-1]
                                avg_volume = symbol_data['Volume'].mean()
                                
                                # Consider trending if volume is above average or significant price movement
                                volume_ratio = volume / avg_volume if avg_volume > 0 else 1
                                is_trending = volume_ratio > 1.2 or abs(change) > 2
                                
                                if is_trending:
                                    trending.append({
                                        "symbol": symbol,
                                        "name": ticker_info.get('longName', symbol),
                                        "exchange": ticker_info.get('exchange', 'NASDAQ'),
                                        "category": "US Stocks",
                                        "price": current_price,
                                        "change_24h": change,
                                        "volume": volume,
                                        "volume_ratio": volume_ratio,
                                        "market_cap": ticker_info.get('marketCap', 0)
                                    })
                    except Exception as e:
                        logger.warning(f"Failed to process trending data for {symbol}: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"Failed to get trending from yfinance: {e}")
        
        # Get trending from CCXT if available
        if CCXT_AVAILABLE and self._exchange:
            try:
                # Get tickers with volume
                tickers = self._exchange.fetch_tickers()
                
                # Sort by volume and get top markets
                sorted_tickers = sorted(
                    [(symbol, data) for symbol, data in tickers.items() if data.get('quoteVolume', 0) > 0],
                    key=lambda x: x[1].get('quoteVolume', 0),
                    reverse=True
                )[:3]  # Top 3 crypto by volume
                
                for symbol, ticker in sorted_tickers:
                    market = self._exchange.markets.get(symbol, {})
                    trending.append({
                        "symbol": symbol.replace('/', '-'),
                        "name": f"{market.get('base', '')} / {market.get('quote', '')}",
                        "exchange": self._exchange.name,
                        "category": "Cryptocurrencies",
                        "price": ticker.get('last', 0),
                        "change_24h": ticker.get('percentage', 0),
                        "volume": ticker.get('quoteVolume', 0)
                    })
            except Exception as e:
                logger.error(f"Failed to get CCXT trending: {e}")
        
        # If no real data, return fallback
        if not trending:
            trending = [
                {"symbol": "BTC-USD", "name": "Bitcoin USD", "exchange": "Crypto", "category": "Cryptocurrencies"},
                {"symbol": "TSLA", "name": "Tesla Inc.", "exchange": "NASDAQ", "category": "US Stocks"},
                {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ", "category": "US Stocks"},
            ]
        
        return trending
    
    def export_markets_list(self, filename: str = None) -> str:
        """
        Export all available markets to a JSON file
        
        Args:
            filename: Output filename
            
        Returns:
            Filename if successful, None if failed
        """
        if filename is None:
            filename = f"markets_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            all_markets = self.get_all_available_markets()
            
            export_data = {
                "export_date": datetime.now().isoformat(),
                "data_source": self.data_source,
                "total_markets": sum(len(markets) for markets in all_markets.values()),
                "categories": len(all_markets),
                "markets": all_markets
            }
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"✅ Markets list exported to {filename}")
            return filename
        except Exception as e:
            print(f"❌ Failed to export markets: {e}")
            return None

# Convenience functions for easy access
def get_popular_markets(data_source: str = 'auto') -> Dict[str, List[Dict[str, str]]]:
    """Get popular markets for a data source"""
    discovery = MarketDiscovery(data_source)
    return discovery.get_popular_markets()

def search_markets(query: str, data_source: str = 'auto', limit: int = 50) -> List[Dict[str, str]]:
    """Search for markets"""
    discovery = MarketDiscovery(data_source)
    return discovery.search_markets(query, limit)

def validate_symbol(symbol: str) -> bool:
    """Validate a market symbol"""
    discovery = MarketDiscovery()
    return discovery.validate_symbol(symbol)

def get_trending_markets(data_source: str = 'auto') -> List[Dict[str, str]]:
    """Get trending markets"""
    discovery = MarketDiscovery(data_source)
    return discovery.get_trending_markets()

def download_market_data(symbols: List[str], period: str = '1mo', interval: str = '1d'):
    """Download historical data using yfinance bulk download"""
    discovery = MarketDiscovery('yfinance')
    return discovery.download_historical_data(symbols, period, interval)

def get_detailed_info(symbol: str) -> Optional[Dict]:
    """Get comprehensive market information including analyst targets, calendar, etc."""
    discovery = MarketDiscovery('yfinance')
    return discovery.get_detailed_market_info(symbol)

def get_fund_info(symbol: str) -> Optional[Dict]:
    """Get ETF/Fund data including holdings and sector weightings"""
    discovery = MarketDiscovery('yfinance')
    return discovery.get_fund_data(symbol)

def get_options_chain(symbol: str) -> Optional[Dict]:
    """Get options chain data for a symbol"""
    discovery = MarketDiscovery('yfinance')
    return discovery.get_options_data(symbol)