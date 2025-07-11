import streamlit as st
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import page modules
from src.gui.pages.dashboard import render_dashboard
from src.gui.pages.markets import render_markets
from src.gui.pages.strategies import render_strategies
from src.gui.pages.backtesting import render_backtesting
from src.gui.pages.settings import render_settings

st.set_page_config(
    page_title="Backtrader Alerts System", 
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_page_config():
    """Get page configuration mapping"""
    return {
        "Dashboard": {
            "function": render_dashboard,
            "icon": "📊",
            "description": "Main overview and live alerts"
        },
        "Markets": {
            "function": render_markets,
            "icon": "🏪",
            "description": "Discover and browse trading markets"
        },
        "Strategies": {
            "function": render_strategies,
            "icon": "🎯",
            "description": "Configure and manage trading strategies"
        },
        "Backtesting": {
            "function": render_backtesting,
            "icon": "🧪",
            "description": "Test strategies with historical data"
        },
        "Settings": {
            "function": render_settings,
            "icon": "⚙️",
            "description": "Application configuration and preferences"
        }
    }

def render_navigation():
    """Render the sidebar navigation"""
    pages_config = get_page_config()
    
    with st.sidebar:
        st.title("🚀 Backtrader Alerts")
        st.write("Professional Trading System")
        
        # Page selection
        st.subheader("📋 Navigation")
        
        # Get current page from session state or default to Dashboard
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'Dashboard'
        
        # Create navigation buttons
        for page_name, page_info in pages_config.items():
            # Create button with icon and description
            button_label = f"{page_info['icon']} {page_name}"
            
            if st.button(
                button_label, 
                key=f"nav_{page_name}",
                use_container_width=True,
                type="primary" if st.session_state.current_page == page_name else "secondary"
            ):
                st.session_state.current_page = page_name
                st.rerun()
            
            # Show description as caption
            if st.session_state.current_page == page_name:
                st.caption(f"📝 {page_info['description']}")
        
        st.divider()
        
        # Quick stats
        st.subheader("📊 Quick Stats")
        st.metric("System Status", "🟢 Online")
        st.metric("Active Strategies", "3")
        st.metric("Today's Signals", "7")
        
        st.divider()
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.toast("Data refreshed!", icon="✅")
        
        if st.button("📊 Run Quick Backtest", use_container_width=True):
            st.session_state.current_page = 'Backtesting'
            st.rerun()
        
        if st.button("🔍 Discover Markets", use_container_width=True):
            st.session_state.current_page = 'Markets'
            st.rerun()
    
    return st.session_state.current_page

def main():
    """Main application entry point"""
    
    # Render navigation and get current page
    current_page = render_navigation()
    
    # Get page configuration
    pages_config = get_page_config()
    
    # Render the current page
    if current_page in pages_config:
        try:
            # Call the appropriate page render function
            pages_config[current_page]["function"]()
        except Exception as e:
            st.error(f"Error rendering {current_page} page: {str(e)}")
            st.code(f"Error details: {str(e)}", language="text")
    else:
        st.error(f"Page '{current_page}' not found!")
        st.write("Available pages:", list(pages_config.keys()))

if __name__ == "__main__":
    main()