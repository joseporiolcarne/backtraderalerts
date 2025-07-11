# Backtrader Alerts System

A proof of concept that integrates the powerful backtrader library with a modern web frontend. The goal was to build an intuitive UI with Streamlit and Plotly that puts comprehensive trading tools—including backtesting, live alerts, and market data visualization—into a single, web application.

## Features

- **Multiple Data Sources**: Support for Yahoo Finance (stocks/crypto) and Binance (crypto)
- **All Backtrader Indicators**: Support for 30+ indicators including RSI, CCI, Bollinger Bands, MACD, SMA, EMA, and more
- **Multi-Timeframe Analysis**: Analyze multiple timeframes simultaneously (5m, 15m, 30m, 1h, 2h, 4h, 1d)
- **Flexible Strategies**: 
  - Simple Indicator Strategy: Single indicator with customizable entry/exit conditions
  - RSI Crossover Strategy: Classic oversold/overbought strategy
  - Multi-Indicator Strategy: Combine multiple indicators with complex conditions
  - Multi-Timeframe Strategy: Cross-timeframe analysis and alerts
- **Telegram Alerts**: Real-time trade notifications via Telegram
- **Streamlit GUI**: Interactive web interface for backtesting and analysis
- **CLI Support**: Command-line interface for automated workflows
- **Comprehensive Results**: Detailed trade history, performance metrics, and visualizations

<img width="1852" height="823" alt="image" src="https://github.com/user-attachments/assets/7d46db89-cd09-43f9-9681-ad6cbe633f69" />

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/backtraderalerts.git
cd backtraderalerts
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure settings (optional):
```bash
cp config/config.yaml.example config/config.yaml
# Edit config/config.yaml with your settings
```

## Quick Start

### GUI Mode (Recommended)

Launch the Streamlit interface:
```bash
python main.py --mode gui
```

Or directly:
```bash
streamlit run src/gui/streamlit_app.py
```

### CLI Mode

Run a backtest from the command line:
```bash
python main.py --mode backtest --symbol BTC-USD --interval 1d --start-date 2023-01-01
```

## Configuration

### Telegram Setup

1. Create a Telegram bot:
   - Message @BotFather on Telegram
   - Use `/newbot` command
   - Save the bot token

2. Get your chat ID:
   - Message your bot
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find your chat ID in the response

3. Add to configuration:
   - In GUI: Enter in the sidebar
   - In config file: Update `telegram` section

### Available Indicators

The system supports all major Backtrader indicators organized by category:

**Momentum Indicators:**
- RSI, CCI, Stochastic, Williams %R, ROC

**Trend Indicators:**
- SMA, EMA, WMA, DEMA, TEMA, ADX, MACD, Ichimoku

**Volatility Indicators:**
- Bollinger Bands, ATR, Standard Deviation, Keltner Channel, Donchian Channel

**Volume Indicators:**
- OBV, A/D, MFI, Chaikin Money Flow

**Other Indicators:**
- Parabolic SAR, Pivot Points, ZigZag

### Strategy Types

1. **Simple Indicator Strategy**: Use any single indicator with customizable entry/exit rules
2. **RSI Crossover Strategy**: Classic RSI oversold/overbought strategy  
3. **Multi-Indicator Strategy**: Combine multiple indicators with complex conditions (AND/OR logic, crossovers)
4. **Multi-Timeframe Strategy**: Analyze multiple timeframes simultaneously with conditions like:
   - "Buy when 1h close > SMA(200) AND 4h RSI < 30"
   - "Sell when daily close crosses below EMA(50)"
   - "Alert when 4h price crosses above $50,000"

## Project Structure

```
backtraderalerts/
├── src/
│   ├── data/            # Data fetching modules
│   ├── strategies/      # Trading strategies
│   ├── alerts/          # Alert dispatchers
│   ├── engine/          # Backtrader engine
│   ├── gui/             # Streamlit interface
│   └── config/          # Configuration management
├── config/              # Configuration files
├── logs/                # Log files
├── main.py              # Main entry point
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Usage Examples

### GUI Workflow

1. **Configure Settings**:
   - Open sidebar
   - Enter Telegram credentials (optional)
   - Set trading parameters

2. **Run Backtest**:
   - Select symbol and date range
   - Configure strategy parameters
   - Click "Run Backtest"

3. **Analyze Results**:
   - View portfolio performance chart
   - Check buy/sell signals on price chart
   - Review trade history table
   - Download results as CSV

### CLI Examples

Basic backtest:
```bash
python main.py --mode backtest --symbol AAPL --interval 1d
```

With custom parameters:
```bash
python main.py --mode backtest \
    --symbol BTC-USD \
    --interval 4h \
    --start-date 2023-06-01 \
    --end-date 2023-12-31 \
    --rsi-period 21 \
    --rsi-oversold 25 \
    --rsi-overbought 75
```

Using config file:
```bash
python main.py --mode backtest --config my_config.yaml --symbol ETH-USD
```




## Extending the System

### Adding New Strategies

1. Create a new file in `src/strategies/`
2. Inherit from `backtrader.Strategy`
3. Implement `__init__`, `next`, and optional logging methods
4. Update GUI to include new strategy option

Example:
```python
class MyStrategy(bt.Strategy):
    params = (
        ('param1', 10),
        ('param2', 20),
    )
    
    def __init__(self):
        # Initialize indicators
        pass
    
    def next(self):
        # Trading logic
        pass
```

### Adding New Data Sources

1. Update `DataFetcher` class in `src/data/fetcher.py`
2. Add new source to `fetch_data` method
3. Update configuration options

## Troubleshooting

### Common Issues

1. **"No module named 'backtrader'"**
   - Run: `pip install -r requirements.txt`

2. **Telegram alerts not working**
   - Verify bot token and chat ID
   - Check internet connection
   - Ensure bot has messaged you first

3. **Data fetch errors**
   - Check symbol format (e.g., BTC-USD for Yahoo Finance)
   - Verify date range is valid
   - Check internet connection


```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Backtrader](https://www.backtrader.com/) - Python backtesting library
- [Streamlit](https://streamlit.io/) - Web app framework
- [yfinance](https://github.com/ranaroussi/yfinance) - Yahoo Finance data
- [python-telegram-bot](https://python-telegram-bot.org/) - Telegram bot API
