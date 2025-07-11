"""
Backtesting Page - Run and analyze strategy backtests
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys
import os

# Import numpy with fallback
try:
    import numpy as np
except ImportError:
    np = None

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.visualization.trading_charts import TradingCharts

def render_backtesting():
    """Render the backtesting page"""
    st.title("🧪 Backtesting Lab")
    st.write("Test and optimize your trading strategies with historical data")
    
    # Backtest configuration
    st.subheader("🛠️ Backtest Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Strategy selection
        strategy = st.selectbox(
            "Select Strategy",
            ["RSI Crossover", "Moving Average", "Multi-Indicator", "Multi-Timeframe", "Buy & Hold"]
        )
        
        # Symbol selection
        symbol = st.selectbox(
            "Trading Symbol",
            ["AAPL", "BTC-USD", "TSLA", "GOOGL", "ETH-USD", "MSFT", "AMZN"]
        )
        
        # Date range
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=365),
            max_value=datetime.now()
        )
        
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            max_value=datetime.now()
        )
    
    with col2:
        # Trading parameters
        initial_capital = st.number_input(
            "Initial Capital ($)",
            value=10000,
            min_value=1000,
            max_value=1000000,
            step=1000
        )
        
        commission = st.number_input(
            "Commission (%)",
            value=0.1,
            min_value=0.0,
            max_value=1.0,
            step=0.01
        )
        
        position_size = st.selectbox(
            "Position Sizing",
            ["Fixed Amount", "% of Capital", "Equal Weight", "Risk Parity"]
        )
        
        if position_size == "Fixed Amount":
            size_value = st.number_input("Amount per Trade ($)", value=1000, min_value=100)
        elif position_size == "% of Capital":
            size_value = st.slider("% of Capital per Trade", 1, 100, 10)
        else:
            size_value = None
    
    # Advanced settings
    with st.expander("🔧 Advanced Settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            slippage = st.number_input("Slippage (%)", value=0.05, min_value=0.0, max_value=1.0, step=0.01)
            max_positions = st.number_input("Max Concurrent Positions", value=1, min_value=1, max_value=10)
        
        with col2:
            stop_loss = st.number_input("Stop Loss (%)", value=0.0, min_value=0.0, max_value=20.0, step=0.1)
            take_profit = st.number_input("Take Profit (%)", value=0.0, min_value=0.0, max_value=50.0, step=0.1)
    
    # Run backtest button
    if st.button("🚀 Run Backtest", type="primary"):
        run_backtest(strategy, symbol, start_date, end_date, initial_capital, commission)
    
    # Backtest results section
    st.subheader("📈 Backtest Results")
    
    # Check if we have results to display
    if 'backtest_results' not in st.session_state:
        st.info("Configure your backtest parameters above and click 'Run Backtest' to see results.")
        return
    
    results = st.session_state.backtest_results
    
    # Performance metrics
    display_performance_metrics(results)
    
    # Charts
    display_backtest_charts(results)
    
    # Trade analysis
    display_trade_analysis(results)
    
    # Optimization section
    st.subheader("🎯 Strategy Optimization")
    
    with st.expander("Parameter Optimization"):
        st.write("Optimize strategy parameters for better performance")
        
        if strategy == "RSI Crossover":
            col1, col2 = st.columns(2)
            with col1:
                rsi_range = st.slider("RSI Period Range", 5, 50, (10, 20))
            with col2:
                oversold_range = st.slider("Oversold Range", 10, 40, (25, 35))
        
        elif strategy == "Moving Average":
            col1, col2 = st.columns(2)
            with col1:
                fast_ma_range = st.slider("Fast MA Range", 5, 50, (10, 25))
            with col2:
                slow_ma_range = st.slider("Slow MA Range", 20, 100, (40, 60))
        
        if st.button("Optimize Parameters"):
            st.success("Parameter optimization completed! Best parameters highlighted below.")
            
            # Mock optimization results
            optimization_data = {
                "Parameter Set": ["Set 1", "Set 2", "Set 3", "Set 4", "Set 5"],
                "Total Return": ["15.3%", "18.7%", "12.1%", "22.4%", "16.8%"],
                "Sharpe Ratio": [1.23, 1.45, 0.98, 1.67, 1.34],
                "Max Drawdown": ["-8.2%", "-6.5%", "-12.1%", "-5.3%", "-7.8%"]
            }
            
            opt_df = pd.DataFrame(optimization_data)
            st.dataframe(opt_df, use_container_width=True)

def run_backtest(strategy, symbol, start_date, end_date, initial_capital, commission):
    """Run the backtest simulation"""
    
    with st.spinner(f"Running backtest for {strategy} on {symbol}..."):
        import time
        time.sleep(3)  # Simulate backtest processing
        
        # Generate mock backtest results
        results = generate_mock_backtest_results(symbol, start_date, end_date, initial_capital)
        
        # Store results in session state
        st.session_state.backtest_results = results
        
        st.success(f"Backtest completed for {strategy} on {symbol}!")
        st.rerun()

def generate_mock_backtest_results(symbol, start_date, end_date, initial_capital):
    """Generate mock backtest results for demonstration"""
    
    # Generate date range
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Generate portfolio value over time
    portfolio_values = [initial_capital]
    
    if np is not None:
        np.random.seed(42)
        for i in range(1, len(dates)):
            # Random walk with slight upward bias
            daily_return = np.random.normal(0.0008, 0.02)
            new_value = portfolio_values[-1] * (1 + daily_return)
            portfolio_values.append(new_value)
    else:
        # Fallback without numpy
        import random
        random.seed(42)
        for i in range(1, len(dates)):
            daily_return = random.gauss(0.0008, 0.02)
            new_value = portfolio_values[-1] * (1 + daily_return)
            portfolio_values.append(new_value)
    
    portfolio_df = pd.DataFrame({
        'Date': dates,
        'Portfolio_Value': portfolio_values
    }).set_index('Date')
    
    # Generate trades
    if np is not None:
        num_trades = np.random.randint(15, 30)
        trade_dates = np.random.choice(dates[10:-10], num_trades, replace=False)
        trade_dates = sorted(trade_dates)
        
        trades = []
        for i, trade_date in enumerate(trade_dates):
            action = 'BUY' if i % 2 == 0 else 'SELL'
            price = np.random.uniform(90, 110)
            quantity = np.random.randint(1, 10)
            pnl = np.random.normal(50, 200) if action == 'SELL' else 0
    else:
        # Fallback without numpy
        import random
        num_trades = random.randint(15, 30)
        available_dates = dates[10:-10]
        trade_dates = sorted(random.sample(list(available_dates), num_trades))
        
        trades = []
        for i, trade_date in enumerate(trade_dates):
            action = 'BUY' if i % 2 == 0 else 'SELL'
            price = random.uniform(90, 110)
            quantity = random.randint(1, 10)
            pnl = random.gauss(50, 200) if action == 'SELL' else 0
        
        trades.append({
            'Date': trade_date,
            'Action': action,
            'Symbol': symbol,
            'Price': price,
            'Quantity': quantity,
            'PnL': pnl
        })
    
    # Calculate metrics
    total_return = (portfolio_values[-1] - initial_capital) / initial_capital * 100
    
    # Calculate drawdown
    running_max = pd.Series(portfolio_values).expanding().max()
    drawdown = (pd.Series(portfolio_values) - running_max) / running_max * 100
    max_drawdown = drawdown.min()
    
    # Win rate
    winning_trades = [t for t in trades if t['PnL'] > 0]
    win_rate = len(winning_trades) / len([t for t in trades if t['PnL'] != 0]) * 100 if trades else 0
    
    # Sharpe ratio (simplified)
    returns = pd.Series(portfolio_values).pct_change().dropna()
    if np is not None:
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
    else:
        sharpe_ratio = returns.mean() / returns.std() * (252 ** 0.5) if returns.std() > 0 else 0
    
    return {
        'portfolio_value': portfolio_df['Portfolio_Value'],
        'trades': trades,
        'total_return': total_return,
        'max_drawdown': max_drawdown,
        'win_rate': win_rate,
        'sharpe_ratio': sharpe_ratio,
        'initial_capital': initial_capital,
        'final_value': portfolio_values[-1],
        'drawdown': drawdown,
        'num_trades': len(trades)
    }

def display_performance_metrics(results):
    """Display performance metrics"""
    st.subheader("📉 Performance Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Return",
            f"{results['total_return']:.1f}%",
            f"{results['total_return'] - 10:.1f}% vs benchmark"
        )
    
    with col2:
        st.metric(
            "Sharpe Ratio",
            f"{results['sharpe_ratio']:.2f}",
            f"{results['sharpe_ratio'] - 1.0:.2f} vs 1.0"
        )
    
    with col3:
        st.metric(
            "Max Drawdown",
            f"{results['max_drawdown']:.1f}%",
            f"{results['max_drawdown'] + 2:.1f}% vs -10%"
        )
    
    with col4:
        st.metric(
            "Win Rate",
            f"{results['win_rate']:.0f}%",
            f"{results['win_rate'] - 50:.0f}% vs 50%"
        )
    
    # Additional metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Initial Capital", f"${results['initial_capital']:,.0f}")
    
    with col2:
        st.metric("Final Value", f"${results['final_value']:,.0f}")
    
    with col3:
        st.metric("Total Trades", results['num_trades'])
    
    with col4:
        profit = results['final_value'] - results['initial_capital']
        st.metric("Profit/Loss", f"${profit:,.0f}")

def display_backtest_charts(results):
    """Display backtest charts"""
    st.subheader("📈 Performance Charts")
    
    # Portfolio value chart
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=["Portfolio Value Over Time", "Drawdown"]
    )
    
    # Portfolio value
    fig.add_trace(
        go.Scatter(
            x=results['portfolio_value'].index,
            y=results['portfolio_value'].values,
            mode='lines',
            name='Portfolio Value',
            line=dict(color='#00C851', width=2)
        ),
        row=1, col=1
    )
    
    # Add trades as markers
    buy_trades = [t for t in results['trades'] if t['Action'] == 'BUY']
    sell_trades = [t for t in results['trades'] if t['Action'] == 'SELL']
    
    if buy_trades:
        buy_dates = [t['Date'] for t in buy_trades]
        buy_values = [results['portfolio_value'].loc[results['portfolio_value'].index >= d].iloc[0] 
                     if len(results['portfolio_value'].loc[results['portfolio_value'].index >= d]) > 0 
                     else results['portfolio_value'].iloc[-1] for d in buy_dates]
        
        fig.add_trace(
            go.Scatter(
                x=buy_dates,
                y=buy_values,
                mode='markers',
                name='Buy Signals',
                marker=dict(symbol='triangle-up', size=8, color='green')
            ),
            row=1, col=1
        )
    
    if sell_trades:
        sell_dates = [t['Date'] for t in sell_trades]
        sell_values = [results['portfolio_value'].loc[results['portfolio_value'].index >= d].iloc[0] 
                      if len(results['portfolio_value'].loc[results['portfolio_value'].index >= d]) > 0 
                      else results['portfolio_value'].iloc[-1] for d in sell_dates]
        
        fig.add_trace(
            go.Scatter(
                x=sell_dates,
                y=sell_values,
                mode='markers',
                name='Sell Signals',
                marker=dict(symbol='triangle-down', size=8, color='red')
            ),
            row=1, col=1
        )
    
    # Drawdown
    fig.add_trace(
        go.Scatter(
            x=results['portfolio_value'].index,
            y=results['drawdown'],
            mode='lines',
            name='Drawdown',
            line=dict(color='red', width=1),
            fill='tozeroy',
            fillcolor='rgba(255, 0, 0, 0.1)'
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        title="Backtest Performance Analysis",
        template="plotly_dark",
        height=600,
        showlegend=True
    )
    
    fig.update_yaxes(title_text="Portfolio Value ($)", row=1, col=1)
    fig.update_yaxes(title_text="Drawdown (%)", row=2, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)

def display_trade_analysis(results):
    """Display trade analysis"""
    st.subheader("📋 Trade Analysis")
    
    if not results['trades']:
        st.info("No trades executed in this backtest.")
        return
    
    # Trade distribution
    col1, col2 = st.columns(2)
    
    with col1:
        # PnL distribution
        trade_pnls = [t['PnL'] for t in results['trades'] if t['PnL'] != 0]
        
        if trade_pnls:
            fig = go.Figure(data=[go.Histogram(x=trade_pnls, nbinsx=20)])
            fig.update_layout(
                title="Trade P&L Distribution",
                xaxis_title="P&L ($)",
                yaxis_title="Frequency",
                template="plotly_dark",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Win/Loss ratio
        winning_trades = [t for t in results['trades'] if t['PnL'] > 0]
        losing_trades = [t for t in results['trades'] if t['PnL'] < 0]
        
        fig = go.Figure(data=[go.Pie(
            labels=['Winning Trades', 'Losing Trades'],
            values=[len(winning_trades), len(losing_trades)],
            hole=0.3
        )])
        
        fig.update_layout(
            title="Win/Loss Distribution",
            template="plotly_dark",
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Trade table
    st.subheader("📋 Recent Trades")
    
    trades_df = pd.DataFrame(results['trades'])
    trades_df['Date'] = pd.to_datetime(trades_df['Date']).dt.strftime('%Y-%m-%d')
    trades_df['Price'] = trades_df['Price'].apply(lambda x: f"${x:.2f}")
    trades_df['PnL'] = trades_df['PnL'].apply(lambda x: f"${x:.2f}" if x != 0 else "-")
    
    # Show last 10 trades
    st.dataframe(trades_df.tail(10), use_container_width=True)

if __name__ == "__main__":
    render_backtesting()