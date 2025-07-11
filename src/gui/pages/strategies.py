"""
Strategies Page - Configure and manage trading strategies
"""
import streamlit as st
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.config.config_manager import ConfigManager
from src.alerts.alert_manager import AlertManager

def render_strategies():
    """Render the strategies configuration page"""
    st.title("🎯 Trading Strategies")
    st.write("Configure and manage your trading strategies")
    
    # Strategy selection
    st.subheader("🛠️ Strategy Configuration")
    
    strategy_type = st.selectbox(
        "Select Strategy Type",
        ["RSI Crossover", "Moving Average", "Multi-Indicator", "Multi-Timeframe", "Custom"]
    )
    
    # Strategy-specific configuration
    if strategy_type == "RSI Crossover":
        render_rsi_strategy()
    elif strategy_type == "Moving Average":
        render_ma_strategy()
    elif strategy_type == "Multi-Indicator":
        render_multi_indicator_strategy()
    elif strategy_type == "Multi-Timeframe":
        render_multi_timeframe_strategy()
    elif strategy_type == "Custom":
        render_custom_strategy()
    
    # Active strategies overview
    st.subheader("📊 Active Strategies")
    
    # Mock active strategies data
    active_strategies = [
        {"Name": "RSI_Oversold_AAPL", "Symbol": "AAPL", "Type": "RSI Crossover", "Status": "Active", "Signals": 5},
        {"Name": "MA_Cross_BTC", "Symbol": "BTC-USD", "Type": "Moving Average", "Status": "Active", "Signals": 3},
        {"Name": "Multi_TF_TSLA", "Symbol": "TSLA", "Type": "Multi-Timeframe", "Status": "Paused", "Signals": 8},
    ]
    
    for strategy in active_strategies:
        with st.container():
            col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1, 1])
            
            with col1:
                st.write(f"**{strategy['Name']}**")
            
            with col2:
                st.write(strategy['Symbol'])
            
            with col3:
                st.write(strategy['Type'])
            
            with col4:
                if strategy['Status'] == 'Active':
                    st.success(strategy['Status'])
                else:
                    st.warning(strategy['Status'])
            
            with col5:
                st.metric("Signals", strategy['Signals'])
            
            with col6:
                if st.button("⏸️", key=f"pause_{strategy['Name']}"):
                    st.warning(f"Paused {strategy['Name']}")
            
            st.divider()
    
    # Strategy performance
    st.subheader("📈 Strategy Performance")
    
    # Performance metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Strategies", "3", "0")
    
    with col2:
        st.metric("Active", "2", "+1")
    
    with col3:
        st.metric("Total Signals", "16", "+3")
    
    with col4:
        st.metric("Success Rate", "72%", "+5%")
    
    # Strategy backtesting
    st.subheader("🧪 Backtesting")
    
    col1, col2 = st.columns(2)
    
    with col1:
        backtest_symbol = st.selectbox("Select Symbol", ["AAPL", "BTC-USD", "TSLA", "GOOGL"])
        backtest_period = st.selectbox("Backtest Period", ["1 Month", "3 Months", "6 Months", "1 Year"])
    
    with col2:
        initial_capital = st.number_input("Initial Capital ($)", value=10000, min_value=1000)
        commission = st.number_input("Commission (%)", value=0.1, min_value=0.0, max_value=1.0, step=0.01)
    
    if st.button("Run Backtest", type="primary"):
        with st.spinner("Running backtest..."):
            import time
            time.sleep(2)  # Simulate backtest
            
            st.success("Backtest completed!")
            
            # Mock backtest results
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Return", "15.3%", "2.1%")
            
            with col2:
                st.metric("Win Rate", "68%", "3%")
            
            with col3:
                st.metric("Max Drawdown", "-8.2%", "1.1%")
            
            with col4:
                st.metric("Sharpe Ratio", "1.45", "0.12")

def render_rsi_strategy():
    """Render RSI strategy configuration"""
    st.write("**RSI Crossover Strategy Configuration**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        rsi_period = st.number_input("RSI Period", value=14, min_value=5, max_value=50)
    
    with col2:
        rsi_oversold = st.number_input("Oversold Level", value=30, min_value=10, max_value=40)
    
    with col3:
        rsi_overbought = st.number_input("Overbought Level", value=70, min_value=60, max_value=90)
    
    # Symbol selection
    symbol = st.text_input("Trading Symbol", value="AAPL", placeholder="e.g., AAPL, BTC-USD")
    
    # Alert configuration
    st.subheader("🔔 Alert Settings")
    
    alert_on_entry = st.checkbox("Alert on Entry Signal", value=True)
    alert_on_exit = st.checkbox("Alert on Exit Signal", value=True)
    
    if st.button("Save RSI Strategy"):
        st.success(f"RSI strategy saved for {symbol}!")
        
        # Mock configuration save
        config_data = {
            "strategy_type": "RSI Crossover",
            "symbol": symbol,
            "rsi_period": rsi_period,
            "rsi_oversold": rsi_oversold,
            "rsi_overbought": rsi_overbought,
            "alert_on_entry": alert_on_entry,
            "alert_on_exit": alert_on_exit
        }
        
        st.json(config_data)

def render_ma_strategy():
    """Render Moving Average strategy configuration"""
    st.write("**Moving Average Strategy Configuration**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fast_ma = st.number_input("Fast MA Period", value=20, min_value=5, max_value=100)
        ma_type = st.selectbox("MA Type", ["SMA", "EMA", "WMA"])
    
    with col2:
        slow_ma = st.number_input("Slow MA Period", value=50, min_value=10, max_value=200)
        signal_type = st.selectbox("Signal Type", ["Crossover", "Price Above/Below", "Both"])
    
    symbol = st.text_input("Trading Symbol", value="BTC-USD", placeholder="e.g., BTC-USD, TSLA")
    
    if st.button("Save MA Strategy"):
        st.success(f"Moving Average strategy saved for {symbol}!")

def render_multi_indicator_strategy():
    """Render Multi-Indicator strategy configuration"""
    st.write("**Multi-Indicator Strategy Configuration**")
    
    # Indicator selection
    st.subheader("📈 Select Indicators")
    
    indicators = st.multiselect(
        "Choose Indicators",
        ["RSI", "MACD", "Bollinger Bands", "Stochastic", "CCI", "ADX", "ATR"],
        default=["RSI", "MACD"]
    )
    
    # Configure each selected indicator
    for indicator in indicators:
        with st.expander(f"Configure {indicator}"):
            if indicator == "RSI":
                st.number_input(f"{indicator} Period", value=14, key=f"{indicator}_period")
                st.slider(f"{indicator} Oversold", 10, 40, 30, key=f"{indicator}_oversold")
                st.slider(f"{indicator} Overbought", 60, 90, 70, key=f"{indicator}_overbought")
            elif indicator == "MACD":
                st.number_input("Fast Period", value=12, key="macd_fast")
                st.number_input("Slow Period", value=26, key="macd_slow")
                st.number_input("Signal Period", value=9, key="macd_signal")
            else:
                st.number_input(f"{indicator} Period", value=14, key=f"{indicator}_period")
    
    # Condition logic
    st.subheader("🧩 Strategy Logic")
    
    logic_type = st.selectbox("Condition Logic", ["ALL conditions must be true (AND)", "ANY condition can be true (OR)"])
    
    symbol = st.text_input("Trading Symbol", value="AAPL", placeholder="e.g., AAPL, ETH-USD")
    
    if st.button("Save Multi-Indicator Strategy"):
        st.success(f"Multi-Indicator strategy saved for {symbol}!")

def render_multi_timeframe_strategy():
    """Render Multi-Timeframe strategy configuration"""
    st.write("**Multi-Timeframe Strategy Configuration**")
    
    # Timeframe selection
    st.subheader("⏰ Timeframe Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tf1 = st.selectbox("Primary Timeframe", ["1m", "5m", "15m", "1h", "4h", "1d"], index=3)
        tf1_indicator = st.selectbox("Primary Indicator", ["RSI", "SMA", "EMA", "MACD"])
    
    with col2:
        tf2 = st.selectbox("Secondary Timeframe", ["1m", "5m", "15m", "1h", "4h", "1d"], index=4)
        tf2_indicator = st.selectbox("Secondary Indicator", ["RSI", "SMA", "EMA", "MACD"], key="tf2_ind")
    
    with col3:
        tf3 = st.selectbox("Tertiary Timeframe", ["1m", "5m", "15m", "1h", "4h", "1d"], index=5)
        tf3_indicator = st.selectbox("Tertiary Indicator", ["RSI", "SMA", "EMA", "MACD"], key="tf3_ind")
    
    # Coordination logic
    st.subheader("🔄 Timeframe Coordination")
    
    coordination = st.selectbox(
        "Timeframe Coordination",
        ["All timeframes must align", "Majority timeframes (2/3)", "Any timeframe signal"]
    )
    
    symbol = st.text_input("Trading Symbol", value="TSLA", placeholder="e.g., TSLA, BTC-USD")
    
    if st.button("Save Multi-Timeframe Strategy"):
        st.success(f"Multi-Timeframe strategy saved for {symbol}!")

def render_custom_strategy():
    """Render Custom strategy configuration"""
    st.write("**Custom Strategy Configuration**")
    
    st.info("💡 Create your own strategy using custom conditions")
    
    # Strategy name
    strategy_name = st.text_input("Strategy Name", placeholder="e.g., My Custom Strategy")
    
    # Custom conditions
    st.subheader("📋 Entry Conditions")
    
    entry_conditions = st.text_area(
        "Entry Conditions (Python-like syntax)",
        placeholder="Example:\nrsi < 30 AND\nsma_20 > sma_50 AND\nvolume > average_volume * 1.5",
        height=100
    )
    
    st.subheader("📊 Exit Conditions")
    
    exit_conditions = st.text_area(
        "Exit Conditions (Python-like syntax)",
        placeholder="Example:\nrsi > 70 OR\nprofit > 5% OR\nloss > 2%",
        height=100
    )
    
    # Risk management
    st.subheader("⚠️ Risk Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        stop_loss = st.number_input("Stop Loss (%)", value=2.0, min_value=0.1, max_value=10.0, step=0.1)
    
    with col2:
        take_profit = st.number_input("Take Profit (%)", value=5.0, min_value=0.1, max_value=20.0, step=0.1)
    
    symbol = st.text_input("Trading Symbol", placeholder="e.g., AAPL, BTC-USD")
    
    if st.button("Save Custom Strategy"):
        if strategy_name and entry_conditions and symbol:
            st.success(f"Custom strategy '{strategy_name}' saved for {symbol}!")
        else:
            st.warning("Please fill in all required fields.")

if __name__ == "__main__":
    render_strategies()