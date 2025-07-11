"""
Dashboard Page - Main overview of the trading system
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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

from src.data.market_discovery import MarketDiscovery
from src.visualization.trading_charts import TradingCharts, create_sample_chart
from src.alerts.alert_manager import AlertManager
from src.config.config_manager import ConfigManager

def render_dashboard():
    """Render the main dashboard page"""
    st.title("🚀 Backtrader Alerts - Trading Dashboard")
    
    # Sidebar with quick stats
    with st.sidebar:
        st.header("📊 Quick Stats")
        
        # System status
        st.metric("System Status", "🟢 Online")
        
        # Market discovery stats
        discovery = MarketDiscovery()
        markets = discovery.get_all_available_markets()
        total_markets = sum(len(m) for m in markets.values())
        st.metric("Available Markets", total_markets)
        
        # Active alerts (mock for now)
        st.metric("Active Alerts", "3")
        st.metric("Today's Signals", "7")
    
    # Main content area with tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🔥 Trending", "📊 Performance", "⚡ Live Alerts"])
    
    with tab1:
        render_overview_tab()
    
    with tab2:
        render_trending_tab()
    
    with tab3:
        render_performance_tab()
    
    with tab4:
        render_alerts_tab()

def render_overview_tab():
    """Render the overview tab"""
    st.subheader("Market Overview")
    
    # Market categories overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏪 Market Categories")
        discovery = MarketDiscovery()
        categories = discovery.get_market_categories()
        
        for category in categories:
            markets = discovery.get_markets_by_category(category)
            with st.expander(f"{category} ({len(markets)} markets)"):
                for market in markets[:5]:  # Show first 5
                    st.write(f"**{market['symbol']}** - {market['name']}")
                if len(markets) > 5:
                    st.write(f"... and {len(markets) - 5} more")
    
    with col2:
        st.subheader("📈 Sample Chart")
        # Create a sample chart
        try:
            fig = create_sample_chart("BTC-USD")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating chart: {e}")
            st.info("Chart functionality requires plotly. Install with: pip install plotly")
    
    # Recent activity with real market data
    st.subheader("🕐 Recent Activity")
    
    # Get some real market data for activity
    activity_data = []
    popular = discovery.get_popular_markets()
    
    # Create activity from real market movements
    for category, markets in popular.items():
        for market in markets[:2]:  # Get 2 from each category
            if 'price' in market and market['price'] > 0:
                change = market.get('change_24h', 0)
                if abs(change) > 2:  # Significant movement
                    event = "Price surge alert" if change > 0 else "Price drop alert"
                    activity_data.append({
                        "Symbol": market['symbol'],
                        "Event": event,
                        "Price": f"${market['price']:.2f}" if market['price'] > 10 else f"${market['price']:.4f}",
                        "Change": f"{change:+.2f}%"
                    })
    
    # Limit to recent activity
    if activity_data:
        df_activity = pd.DataFrame(activity_data[:8])  # Show top 8
        st.dataframe(df_activity, use_container_width=True)
    else:
        # Fallback if no real data
        st.info("Loading market activity...")

def render_trending_tab():
    """Render the trending markets tab"""
    st.subheader("🔥 Trending Markets")
    
    # Data source selection
    data_source = st.selectbox(
        "Data Source",
        ["auto", "yfinance", "binance"],
        key="trending_data_source"
    )
    
    discovery = MarketDiscovery(data_source)
    trending = discovery.get_trending_markets()
    
    # Display trending markets in a nice grid
    cols = st.columns(4)
    for i, market in enumerate(trending[:8]):  # Show top 8
        with cols[i % 4]:
            # Use real price data if available
            price = market.get('price', 0)
            change = market.get('change_24h', 0)
            
            # Color based on change
            color = "🟢" if change >= 0 else "🔴"
            
            # Format price
            if price > 0:
                price_str = f"${price:.2f}" if price > 10 else f"${price:.4f}"
            else:
                price_str = "$--"
            
            st.metric(
                label=f"{color} {market['symbol']}",
                value=price_str,
                delta=f"{change:+.2f}%" if change != 0 else "--"
            )
            st.caption(market['name'])
            
            # Show volume if available
            if 'volume' in market and market['volume'] > 0:
                if market['volume'] > 1000000:
                    vol_str = f"Vol: ${market['volume']/1000000:.1f}M"
                else:
                    vol_str = f"Vol: ${market['volume']:,.0f}"
                st.caption(vol_str)
    
    # Market heatmap (placeholder)
    st.subheader("📊 Market Heatmap")
    st.info("Market heatmap visualization would appear here with real-time data")
    
    # Sector performance
    st.subheader("🏭 Sector Performance")
    sector_data = {
        "Technology": 2.3,
        "Healthcare": 1.8,
        "Finance": -0.5,
        "Energy": 3.2,
        "Consumer": 0.8,
        "Crypto": -2.1
    }
    
    cols = st.columns(3)
    for i, (sector, performance) in enumerate(sector_data.items()):
        with cols[i % 3]:
            color = "🟢" if performance >= 0 else "🔴"
            st.metric(
                label=f"{color} {sector}",
                value=f"{performance:+.1f}%",
                delta=None
            )

def render_performance_tab():
    """Render the performance analysis tab"""
    st.subheader("📊 Performance Analytics")
    
    # Performance metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Return", "15.3%", "2.1%")
    
    with col2:
        st.metric("Win Rate", "68%", "3%")
    
    with col3:
        st.metric("Sharpe Ratio", "1.45", "0.12")
    
    with col4:
        st.metric("Max Drawdown", "-8.2%", "1.1%")
    
    # Performance chart placeholder
    st.subheader("📈 Portfolio Performance")
    
    # Generate sample performance data
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    portfolio_value = [10000]
    
    if np is not None:
        for i in range(1, len(dates)):
            # Random walk with slight upward bias
            change = np.random.normal(0.0005, 0.015)
            new_value = portfolio_value[-1] * (1 + change)
            portfolio_value.append(new_value)
    else:
        # Fallback without numpy
        import random
        random.seed(42)
        for i in range(1, len(dates)):
            change = random.gauss(0.0005, 0.015)
            new_value = portfolio_value[-1] * (1 + change)
            portfolio_value.append(new_value)
    
    portfolio_df = pd.DataFrame({
        'Date': dates,
        'Portfolio Value': portfolio_value
    })
    
    # Create performance chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=portfolio_df['Date'],
        y=portfolio_df['Portfolio Value'],
        mode='lines',
        name='Portfolio Value',
        line=dict(color='#00C851', width=2),
        fill='tonexty'
    ))
    
    fig.update_layout(
        title="Portfolio Performance Over Time",
        template="plotly_dark",
        height=400,
        xaxis_title="Date",
        yaxis_title="Portfolio Value ($)"
    )
    
    try:
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.error("Error displaying performance chart")
    
    # Strategy performance breakdown
    st.subheader("🎯 Strategy Performance")
    
    strategy_data = {
        "RSI Crossover": {"trades": 23, "win_rate": 65, "profit": 850},
        "Moving Average": {"trades": 18, "win_rate": 72, "profit": 1200},
        "Multi-Timeframe": {"trades": 15, "win_rate": 60, "profit": 980},
    }
    
    for strategy, metrics in strategy_data.items():
        with st.expander(f"📊 {strategy}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Trades", metrics["trades"])
            with col2:
                st.metric("Win Rate", f"{metrics['win_rate']}%")
            with col3:
                st.metric("Profit", f"${metrics['profit']}")

def render_alerts_tab():
    """Render the live alerts tab"""
    st.subheader("⚡ Live Alert Feed")
    
    # Alert configuration section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Recent alerts
        st.subheader("📨 Recent Alerts")
        
        # Mock recent alerts data
        alerts_data = [
            {
                "Time": "11:15:23",
                "Type": "🚨 Trade Signal",
                "Message": "BUY signal for AAPL at $150.25",
                "Status": "Active"
            },
            {
                "Time": "11:10:45",
                "Type": "📊 RSI Alert",
                "Message": "BTC-USD RSI dropped below 30 (oversold)",
                "Status": "Triggered"
            },
            {
                "Time": "11:05:12",
                "Type": "🔔 Price Alert",
                "Message": "TSLA crossed above $220 resistance",
                "Status": "Triggered"
            },
            {
                "Time": "10:58:30",
                "Type": "⚠️ System",
                "Message": "Multi-timeframe strategy activated",
                "Status": "Info"
            },
            {
                "Time": "10:45:18",
                "Type": "🚨 Trade Signal",
                "Message": "SELL signal for ETH-USD at $2,450",
                "Status": "Executed"
            }
        ]
        
        # Display alerts in a container with auto-refresh feel
        alert_container = st.container()
        
        with alert_container:
            for alert in alerts_data:
                # Create alert card
                with st.container():
                    col_time, col_content, col_status = st.columns([1, 3, 1])
                    
                    with col_time:
                        st.caption(alert["Time"])
                    
                    with col_content:
                        st.write(f"{alert['Type']}")
                        st.caption(alert["Message"])
                    
                    with col_status:
                        if alert["Status"] == "Active":
                            st.success(alert["Status"])
                        elif alert["Status"] == "Triggered":
                            st.warning(alert["Status"])
                        elif alert["Status"] == "Executed":
                            st.info(alert["Status"])
                        else:
                            st.caption(alert["Status"])
                
                st.divider()
    
    with col2:
        # Alert statistics
        st.subheader("📈 Alert Stats")
        
        st.metric("Today's Alerts", "12", "+3")
        st.metric("Active Strategies", "4", "0")
        st.metric("Success Rate", "78%", "+5%")
        
        # Alert type distribution
        st.subheader("📊 Alert Types")
        alert_types = {
            "Trade Signals": 45,
            "RSI Alerts": 25,
            "Price Alerts": 20,
            "System": 10
        }
        
        for alert_type, percentage in alert_types.items():
            st.progress(percentage / 100)
            st.caption(f"{alert_type}: {percentage}%")
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        
        if st.button("🔄 Refresh Alerts", type="secondary"):
            st.rerun()
        
        if st.button("⏸️ Pause All Alerts", type="secondary"):
            st.warning("All alerts paused")
        
        if st.button("🧪 Test Alerts", type="secondary"):
            st.success("Test alert sent!")

if __name__ == "__main__":
    render_dashboard()