"""
Markets Page - Simplified market search, add, and management
"""
import streamlit as st
import pandas as pd
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.data.market_discovery import MarketDiscovery, get_detailed_info, download_market_data
from src.visualization.trading_charts import create_sample_chart

def render_markets():
    """Render the simplified markets page"""
    st.title("🏪 Markets")
    st.write("Search and manage your trading markets")
    
    # Initialize session state for added markets
    if 'added_markets' not in st.session_state:
        st.session_state.added_markets = []
    
    # Initialize market discovery
    discovery = MarketDiscovery('auto')
    
    # Search Section
    st.subheader("🔍 Search Markets")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "Search by symbol or name", 
            placeholder="e.g., AAPL, Bitcoin, EUR/USD",
            key="market_search"
        )
    
    with col2:
        search_limit = st.selectbox("Results", [10, 25, 50], index=0)
    
    # Perform search if query provided
    if search_query:
        results = discovery.search_markets(search_query, search_limit)
        
        if results:
            st.write(f"Found {len(results)} results for '{search_query}':")
            
            # Display search results
            for i, result in enumerate(results):
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
                    
                    with col1:
                        st.write(f"**{result['symbol']}**")
                    
                    with col2:
                        st.write(result['name'])
                    
                    with col3:
                        # Show price if available
                        if 'price' in result and result['price'] > 0:
                            price_str = f"${result['price']:.2f}" if result['price'] > 10 else f"${result['price']:.4f}"
                            change = result.get('change_24h', 0)
                            change_color = "🟢" if change >= 0 else "🔴"
                            st.write(f"{price_str} {change_color}{change:+.1f}%")
                        else:
                            st.write(f"{result.get('exchange', 'Market')}")
                    
                    with col4:
                        # Add button
                        if st.button("➕", key=f"add_{result['symbol']}_{i}", help="Add to watchlist"):
                            add_market_to_list(result)
                            st.rerun()
                    
                    st.divider()
        else:
            st.info("No markets found for your search query.")
    else:
        st.info("Enter a symbol or name to search for markets")
    
    # Added Markets Section
    st.subheader("📊 My Markets")
    
    if st.session_state.added_markets:
        st.write(f"You have {len(st.session_state.added_markets)} markets in your watchlist:")
        
        # Display added markets with detailed market data
        for i, market in enumerate(st.session_state.added_markets):
            with st.container():
                # Main row with symbol and name
                col1, col2, col3, col4 = st.columns([2, 3, 1, 1])
                
                with col1:
                    st.write(f"**{market['symbol']}**")
                
                with col2:
                    st.write(market['name'])
                    st.caption(f"Exchange: {market.get('exchange', 'Market')}")
                
                with col3:
                    # View Chart button
                    if st.button("📈", key=f"chart_{market['symbol']}_{i}", help="View chart"):
                        st.session_state['selected_symbol'] = market['symbol']
                        st.session_state['show_chart'] = True
                        st.rerun()
                
                with col4:
                    # Delete button
                    if st.button("🗑️", key=f"delete_{market['symbol']}_{i}", help="Remove from watchlist"):
                        remove_market_from_list(i)
                        st.rerun()
                
                # Market data row
                data_col1, data_col2, data_col3, data_col4, data_col5 = st.columns(5)
                
                with data_col1:
                    # Last Price
                    if 'price' in market and market['price'] > 0:
                        price = market['price']
                        price_str = f"${price:.2f}" if price > 10 else f"${price:.4f}"
                        st.metric("Last Price", price_str)
                    else:
                        st.metric("Last Price", "N/A")
                
                with data_col2:
                    # 24h Change
                    if 'change_24h' in market:
                        change = market['change_24h']
                        if change != 0:
                            st.metric("24h Change", f"{change:+.2f}%", delta=change)
                        else:
                            st.metric("24h Change", "0.00%")
                    else:
                        st.metric("24h Change", "N/A")
                
                with data_col3:
                    # Volume
                    if 'volume' in market and market['volume'] > 0:
                        volume = market['volume']
                        if volume >= 1000000:
                            volume_str = f"${volume/1000000:.1f}M"
                        elif volume >= 1000:
                            volume_str = f"${volume/1000:.1f}K"
                        else:
                            volume_str = f"${volume:,.0f}"
                        st.metric("Volume", volume_str)
                    else:
                        st.metric("Volume", "N/A")
                
                with data_col4:
                    # Market Cap (if available)
                    if 'market_cap' in market and market['market_cap'] > 0:
                        market_cap = market['market_cap']
                        if market_cap >= 1000000000:
                            cap_str = f"${market_cap/1000000000:.1f}B"
                        elif market_cap >= 1000000:
                            cap_str = f"${market_cap/1000000:.1f}M"
                        else:
                            cap_str = f"${market_cap:,.0f}"
                        st.metric("Market Cap", cap_str)
                    else:
                        # Show category instead if no market cap
                        category = market.get('category', 'N/A')
                        st.metric("Category", category)
                
                with data_col5:
                    # Additional data based on market type
                    if 'sector' in market:
                        st.metric("Sector", market['sector'])
                    elif 'base' in market and 'quote' in market:
                        st.metric("Pair", f"{market['base']}/{market['quote']}")
                    else:
                        # Show last update time
                        import datetime
                        now = datetime.datetime.now()
                        update_time = now.strftime("%H:%M")
                        st.metric("Updated", update_time)
                
                st.divider()
        
        # Bulk actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Refresh Prices"):
                refresh_market_prices()
                st.rerun()
        
        with col2:
            if st.button("📤 Export List"):
                export_markets_list()
        
        with col3:
            if st.button("📊 Download Data"):
                download_bulk_data()
        
        # Additional row for more actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔍 Detailed Analysis"):
                show_detailed_analysis()
        
        with col2:
            if st.button("📈 Historical Data"):
                download_historical_data()
        
        with col3:
            if st.button("🗑️ Clear All"):
                if st.session_state.get('confirm_clear', False):
                    st.session_state.added_markets = []
                    st.session_state.confirm_clear = False
                    st.success("All markets cleared!")
                    st.rerun()
                else:
                    st.session_state.confirm_clear = True
                    st.warning("Click again to confirm clearing all markets")
    else:
        st.info("No markets added yet. Search and add markets to your watchlist above.")
        
        # Show some popular suggestions
        st.subheader("💡 Popular Markets")
        popular = discovery.get_popular_markets()
        
        # Show a few popular markets from each category
        suggestions = []
        for category, markets in popular.items():
            if markets:
                suggestions.extend(markets[:2])  # 2 from each category
        
        if suggestions:
            cols = st.columns(min(4, len(suggestions)))
            for i, market in enumerate(suggestions[:4]):
                with cols[i]:
                    st.write(f"**{market['symbol']}**")
                    st.caption(market['name'])
                    if st.button("Add", key=f"suggest_{market['symbol']}"):
                        add_market_to_list(market)
                        st.rerun()
    
    # Chart display if symbol selected
    if st.session_state.get('show_chart', False) and 'selected_symbol' in st.session_state:
        selected_symbol = st.session_state['selected_symbol']
        
        st.subheader(f"📊 Chart for {selected_symbol}")
        
        # Close chart button
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("❌ Close Chart"):
                st.session_state['show_chart'] = False
                st.rerun()
        
        try:
            # Create sample chart
            fig = create_sample_chart(selected_symbol)
            st.plotly_chart(fig, use_container_width=True)
            
            # Market info
            market_info = next((m for m in st.session_state.added_markets if m['symbol'] == selected_symbol), None)
            if market_info:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Symbol", market_info['symbol'])
                with col2:
                    st.metric("Exchange", market_info.get('exchange', 'Market'))
                with col3:
                    if 'price' in market_info and market_info['price'] > 0:
                        price_str = f"${market_info['price']:.2f}" if market_info['price'] > 10 else f"${market_info['price']:.4f}"
                        st.metric("Price", price_str)
        
        except Exception as e:
            st.error(f"Error displaying chart: {e}")
            st.info("Chart functionality requires plotly. Some features may be limited.")

def add_market_to_list(market):
    """Add a market to the watchlist"""
    # Check if already added
    if not any(m['symbol'] == market['symbol'] for m in st.session_state.added_markets):
        st.session_state.added_markets.append(market.copy())
        st.success(f"Added {market['symbol']} to your watchlist!")
    else:
        st.warning(f"{market['symbol']} is already in your watchlist!")

def remove_market_from_list(index):
    """Remove a market from the watchlist"""
    if 0 <= index < len(st.session_state.added_markets):
        removed_market = st.session_state.added_markets.pop(index)
        st.success(f"Removed {removed_market['symbol']} from your watchlist!")

def refresh_market_prices():
    """Refresh prices and market data for all markets in the watchlist"""
    discovery = MarketDiscovery('auto')
    updated_count = 0
    
    with st.spinner("Refreshing market data..."):
        for i, market in enumerate(st.session_state.added_markets):
            try:
                # Search for updated market data
                results = discovery.search_markets(market['symbol'], limit=1)
                if results and len(results) > 0:
                    fresh_data = results[0]
                    
                    # Update with fresh data while preserving original info
                    updated_market = market.copy()
                    updated_market.update(fresh_data)
                    
                    # Ensure we keep the original name if the new one is generic
                    if market.get('name') and len(market['name']) > len(fresh_data.get('name', '')):
                        updated_market['name'] = market['name']
                    
                    st.session_state.added_markets[i] = updated_market
                    updated_count += 1
                    
            except Exception as e:
                # Keep original data if update fails
                continue
    
    if updated_count > 0:
        st.success(f"✅ Updated {updated_count} out of {len(st.session_state.added_markets)} markets!")
    else:
        st.info("ℹ️ No price updates available at the moment. Using cached data.")

def export_markets_list():
    """Export the markets list"""
    if st.session_state.added_markets:
        # Create DataFrame
        df = pd.DataFrame(st.session_state.added_markets)
        
        # Select relevant columns
        export_cols = ['symbol', 'name', 'exchange']
        if 'price' in df.columns:
            export_cols.append('price')
        if 'change_24h' in df.columns:
            export_cols.append('change_24h')
        
        export_df = df[export_cols]
        
        # Convert to CSV
        csv = export_df.to_csv(index=False)
        
        # Download button
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"my_markets_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No markets to export!")

def download_bulk_data():
    """Download bulk market data using yfinance"""
    if not st.session_state.added_markets:
        st.warning("No markets in watchlist to download data for!")
        return
    
    symbols = [market['symbol'] for market in st.session_state.added_markets]
    
    with st.spinner("Downloading market data using yfinance bulk download..."):
        try:
            # Download 1 month of daily data
            data = download_market_data(symbols, period='1mo', interval='1d')
            
            if not data.empty:
                # Convert to CSV for download
                csv_data = data.to_csv()
                
                st.download_button(
                    label="📥 Download Historical Data (CSV)",
                    data=csv_data,
                    file_name=f"market_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                st.success(f"✅ Downloaded data for {len(symbols)} symbols!")
                
                # Show preview
                with st.expander("📊 Data Preview"):
                    st.dataframe(data.head(), use_container_width=True)
            else:
                st.error("Failed to download data. Please check your internet connection.")
        except Exception as e:
            st.error(f"Error downloading data: {e}")

def show_detailed_analysis():
    """Show detailed analysis for selected markets"""
    if not st.session_state.added_markets:
        st.warning("No markets in watchlist to analyze!")
        return
    
    st.subheader("🔍 Detailed Market Analysis")
    
    # Select market for detailed analysis
    symbols = [market['symbol'] for market in st.session_state.added_markets]
    selected_symbol = st.selectbox("Select market for detailed analysis:", symbols)
    
    if selected_symbol:
        with st.spinner(f"Loading detailed information for {selected_symbol}..."):
            try:
                detailed_info = get_detailed_info(selected_symbol)
                
                if detailed_info:
                    # Display key metrics in columns
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Current Price", f"${detailed_info.get('current_price', 0):.2f}")
                        st.metric("52W High", f"${detailed_info.get('52_week_high', 0):.2f}")
                    
                    with col2:
                        st.metric("Market Cap", f"${detailed_info.get('market_cap', 0):,.0f}")
                        st.metric("52W Low", f"${detailed_info.get('52_week_low', 0):.2f}")
                    
                    with col3:
                        st.metric("P/E Ratio", f"{detailed_info.get('pe_ratio', 0):.2f}")
                        st.metric("Beta", f"{detailed_info.get('beta', 0):.2f}")
                    
                    with col4:
                        st.metric("Dividend Yield", f"{detailed_info.get('dividend_yield', 0)*100:.2f}%")
                        st.metric("Volume", f"{detailed_info.get('volume', 0):,.0f}")
                    
                    # Company info
                    if detailed_info.get('business_summary'):
                        with st.expander("📋 Company Overview"):
                            st.write(f"**Sector:** {detailed_info.get('sector', 'N/A')}")
                            st.write(f"**Industry:** {detailed_info.get('industry', 'N/A')}")
                            st.write(f"**Employees:** {detailed_info.get('employees', 0):,}")
                            if detailed_info.get('website'):
                                st.write(f"**Website:** {detailed_info['website']}")
                            st.write("**Business Summary:**")
                            st.write(detailed_info['business_summary'][:500] + "..." if len(detailed_info['business_summary']) > 500 else detailed_info['business_summary'])
                    
                    # Analyst targets
                    if detailed_info.get('target_mean_price', 0) > 0:
                        with st.expander("🎯 Analyst Targets"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Target Low", f"${detailed_info.get('target_low_price', 0):.2f}")
                            with col2:
                                st.metric("Target Mean", f"${detailed_info.get('target_mean_price', 0):.2f}")
                            with col3:
                                st.metric("Target High", f"${detailed_info.get('target_high_price', 0):.2f}")
                            
                            if detailed_info.get('recommendation'):
                                st.write(f"**Recommendation:** {detailed_info['recommendation'].upper()}")
                    
                    # Financial metrics
                    with st.expander("💰 Financial Metrics"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Total Revenue", f"${detailed_info.get('total_revenue', 0):,.0f}")
                            st.metric("Gross Margins", f"{detailed_info.get('gross_margins', 0)*100:.2f}%")
                            st.metric("Trailing EPS", f"${detailed_info.get('trailing_eps', 0):.2f}")
                        with col2:
                            st.metric("Revenue Growth", f"{detailed_info.get('revenue_growth', 0)*100:.2f}%")
                            st.metric("Operating Margins", f"{detailed_info.get('operating_margins', 0)*100:.2f}%")
                            st.metric("Forward EPS", f"${detailed_info.get('forward_eps', 0):.2f}")
                else:
                    st.error(f"Could not retrieve detailed information for {selected_symbol}")
            except Exception as e:
                st.error(f"Error loading detailed analysis: {e}")

def download_historical_data():
    """Download historical data with user-selected parameters"""
    if not st.session_state.added_markets:
        st.warning("No markets in watchlist!")
        return
    
    st.subheader("📈 Download Historical Data")
    
    # Parameters selection
    col1, col2, col3 = st.columns(3)
    
    with col1:
        period = st.selectbox(
            "Time Period", 
            ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'],
            index=2  # Default to 1mo
        )
    
    with col2:
        interval = st.selectbox(
            "Data Interval",
            ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'],
            index=8  # Default to 1d
        )
    
    with col3:
        # Select symbols
        symbols = [market['symbol'] for market in st.session_state.added_markets]
        selected_symbols = st.multiselect("Select Markets", symbols, default=symbols[:3])
    
    if st.button("📊 Download Data", type="primary"):
        if not selected_symbols:
            st.warning("Please select at least one market!")
            return
        
        with st.spinner(f"Downloading {period} data for {len(selected_symbols)} symbols..."):
            try:
                data = download_market_data(selected_symbols, period=period, interval=interval)
                
                if not data.empty:
                    # Show data preview
                    st.success(f"✅ Downloaded {period} data with {interval} intervals!")
                    
                    # Display data info
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Data Points", len(data))
                    with col2:
                        st.metric("Symbols", len(selected_symbols))
                    with col3:
                        st.metric("Date Range", f"{data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")
                    
                    # Data preview
                    with st.expander("📊 Data Preview", expanded=True):
                        st.dataframe(data.head(10), use_container_width=True)
                    
                    # Download buttons
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        csv_data = data.to_csv()
                        st.download_button(
                            label="📥 Download as CSV",
                            data=csv_data,
                            file_name=f"historical_data_{period}_{interval}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    
                    with col2:
                        # Convert to JSON for download
                        json_data = data.to_json(orient='index', date_format='iso')
                        st.download_button(
                            label="📥 Download as JSON",
                            data=json_data,
                            file_name=f"historical_data_{period}_{interval}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                else:
                    st.error("Failed to download data. Please check your parameters and internet connection.")
            except Exception as e:
                st.error(f"Error downloading historical data: {e}")

if __name__ == "__main__":
    render_markets()