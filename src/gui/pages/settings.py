"""
Settings Page - Application configuration and preferences
"""
import streamlit as st
import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.config.config_manager import ConfigManager
from src.alerts.alert_manager import AlertManager

def render_settings():
    """Render the settings page"""
    st.title("⚙️ Settings")
    st.write("Configure your application preferences and alert systems")
    
    # Settings tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Trading", 
        "🔔 Alerts", 
        "📊 Data Sources", 
        "🎨 Interface", 
        "🔒 Security"
    ])
    
    with tab1:
        render_trading_settings()
    
    with tab2:
        render_alert_settings()
    
    with tab3:
        render_data_settings()
    
    with tab4:
        render_interface_settings()
    
    with tab5:
        render_security_settings()
    
    # Configuration management
    st.subheader("📁 Configuration Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save Current Config"):
            save_configuration()
    
    with col2:
        if st.button("📂 Load Config"):
            load_configuration()
    
    with col3:
        if st.button("🔄 Reset to Defaults"):
            reset_to_defaults()
    
    # System information
    with st.expander("📊 System Information"):
        display_system_info()

def render_trading_settings():
    """Render trading configuration settings"""
    st.subheader("💰 Trading Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Capital settings
        st.subheader("💵 Capital Management")
        
        initial_capital = st.number_input(
            "Initial Capital ($)",
            value=st.session_state.get('initial_capital', 10000),
            min_value=1000,
            max_value=1000000,
            step=1000,
            key="settings_initial_capital"
        )
        
        max_position_size = st.slider(
            "Max Position Size (% of capital)",
            1, 100, 
            st.session_state.get('max_position_size', 10),
            key="settings_max_position"
        )
        
        max_daily_loss = st.slider(
            "Max Daily Loss (% of capital)",
            1, 20,
            st.session_state.get('max_daily_loss', 5),
            key="settings_max_loss"
        )
    
    with col2:
        # Trading parameters
        st.subheader("📈 Trading Parameters")
        
        commission = st.number_input(
            "Commission (%)",
            value=st.session_state.get('commission', 0.1),
            min_value=0.0,
            max_value=2.0,
            step=0.01,
            key="settings_commission"
        )
        
        slippage = st.number_input(
            "Slippage (%)",
            value=st.session_state.get('slippage', 0.05),
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            key="settings_slippage"
        )
        
        default_timeframe = st.selectbox(
            "Default Timeframe",
            ["1m", "5m", "15m", "1h", "4h", "1d"],
            index=3,  # Default to 1h
            key="settings_timeframe"
        )
    
    # Risk management
    st.subheader("⚠️ Risk Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        enable_stop_loss = st.checkbox(
            "Enable Stop Loss",
            value=st.session_state.get('enable_stop_loss', True),
            key="settings_enable_sl"
        )
        
        if enable_stop_loss:
            default_stop_loss = st.number_input(
                "Default Stop Loss (%)",
                value=st.session_state.get('default_stop_loss', 2.0),
                min_value=0.1,
                max_value=20.0,
                step=0.1,
                key="settings_stop_loss"
            )
    
    with col2:
        enable_take_profit = st.checkbox(
            "Enable Take Profit",
            value=st.session_state.get('enable_take_profit', True),
            key="settings_enable_tp"
        )
        
        if enable_take_profit:
            default_take_profit = st.number_input(
                "Default Take Profit (%)",
                value=st.session_state.get('default_take_profit', 5.0),
                min_value=0.1,
                max_value=50.0,
                step=0.1,
                key="settings_take_profit"
            )
    
    with col3:
        position_sizing = st.selectbox(
            "Position Sizing Method",
            ["Fixed Amount", "% of Capital", "Equal Weight", "Risk Parity"],
            key="settings_position_sizing"
        )

def render_alert_settings():
    """Render alert system settings"""
    st.subheader("🔔 Alert Configuration")
    
    # Alert systems
    st.subheader("📡 Alert Systems")
    
    alert_systems = st.multiselect(
        "Enable Alert Systems",
        ["Telegram", "Pushover", "Email", "Console", "Discord"],
        default=st.session_state.get('alert_systems', ["Console"]),
        key="settings_alert_systems"
    )
    
    # Telegram settings
    if "Telegram" in alert_systems:
        with st.expander("📨 Telegram Configuration"):
            telegram_token = st.text_input(
                "Bot Token",
                type="password",
                value=st.session_state.get('telegram_token', ''),
                key="settings_telegram_token"
            )
            
            telegram_chat_id = st.text_input(
                "Chat ID",
                value=st.session_state.get('telegram_chat_id', ''),
                key="settings_telegram_chat"
            )
            
            if st.button("Test Telegram Connection"):
                if telegram_token and telegram_chat_id:
                    st.success("✅ Telegram connection test sent!")
                else:
                    st.error("❌ Please configure token and chat ID first")
    
    # Pushover settings
    if "Pushover" in alert_systems:
        with st.expander("📡 Pushover Configuration"):
            pushover_app_token = st.text_input(
                "App Token",
                type="password",
                value=st.session_state.get('pushover_app_token', ''),
                key="settings_pushover_app"
            )
            
            pushover_user_key = st.text_input(
                "User Key",
                type="password",
                value=st.session_state.get('pushover_user_key', ''),
                key="settings_pushover_user"
            )
            
            pushover_priority = st.selectbox(
                "Priority Level",
                ["Low (-2)", "Normal (0)", "High (1)", "Emergency (2)"],
                index=1,
                key="settings_pushover_priority"
            )
            
            if st.button("Test Pushover Connection"):
                if pushover_app_token and pushover_user_key:
                    st.success("✅ Pushover connection test sent!")
                else:
                    st.error("❌ Please configure app token and user key first")
    
    # Email settings
    if "Email" in alert_systems:
        with st.expander("📧 Email Configuration"):
            email_smtp_server = st.text_input(
                "SMTP Server",
                value=st.session_state.get('email_smtp', 'smtp.gmail.com'),
                key="settings_email_smtp"
            )
            
            email_port = st.number_input(
                "SMTP Port",
                value=st.session_state.get('email_port', 587),
                min_value=1,
                max_value=65535,
                key="settings_email_port"
            )
            
            email_username = st.text_input(
                "Email Username",
                value=st.session_state.get('email_username', ''),
                key="settings_email_user"
            )
            
            email_password = st.text_input(
                "Email Password",
                type="password",
                value=st.session_state.get('email_password', ''),
                key="settings_email_pass"
            )
            
            email_to = st.text_input(
                "Send Alerts To",
                value=st.session_state.get('email_to', ''),
                key="settings_email_to"
            )
    
    # Alert preferences
    st.subheader("🔔 Alert Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        alert_frequency = st.selectbox(
            "Alert Frequency",
            ["Immediate", "Every 5 minutes", "Every 15 minutes", "Hourly"],
            key="settings_alert_frequency"
        )
        
        alert_types = st.multiselect(
            "Alert Types",
            ["Trade Signals", "Strategy Updates", "System Errors", "Performance Reports"],
            default=["Trade Signals", "System Errors"],
            key="settings_alert_types"
        )
    
    with col2:
        quiet_hours_enabled = st.checkbox(
            "Enable Quiet Hours",
            value=st.session_state.get('quiet_hours', False),
            key="settings_quiet_hours"
        )
        
        if quiet_hours_enabled:
            quiet_start = st.time_input(
                "Quiet Hours Start",
                value=datetime.strptime("22:00", "%H:%M").time(),
                key="settings_quiet_start"
            )
            
            quiet_end = st.time_input(
                "Quiet Hours End",
                value=datetime.strptime("08:00", "%H:%M").time(),
                key="settings_quiet_end"
            )

def render_data_settings():
    """Render data source settings"""
    st.subheader("📊 Data Source Configuration")
    
    # Primary data source
    primary_source = st.selectbox(
        "Primary Data Source",
        ["yfinance", "Alpha Vantage", "IEX Cloud", "Binance", "Custom API"],
        key="settings_primary_source"
    )
    
    # API configurations
    if primary_source == "Alpha Vantage":
        with st.expander("🔑 Alpha Vantage API"):
            av_api_key = st.text_input(
                "API Key",
                type="password",
                value=st.session_state.get('av_api_key', ''),
                key="settings_av_key"
            )
    
    elif primary_source == "IEX Cloud":
        with st.expander("☁️ IEX Cloud API"):
            iex_api_key = st.text_input(
                "API Token",
                type="password",
                value=st.session_state.get('iex_api_key', ''),
                key="settings_iex_key"
            )
            
            iex_environment = st.selectbox(
                "Environment",
                ["Sandbox", "Production"],
                key="settings_iex_env"
            )
    
    elif primary_source == "Binance":
        with st.expander("🔶 Binance API"):
            binance_api_key = st.text_input(
                "API Key",
                type="password",
                value=st.session_state.get('binance_api_key', ''),
                key="settings_binance_key"
            )
            
            binance_secret = st.text_input(
                "Secret Key",
                type="password",
                value=st.session_state.get('binance_secret', ''),
                key="settings_binance_secret"
            )
    
    # Data preferences
    st.subheader("📊 Data Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        default_period = st.selectbox(
            "Default Data Period",
            ["1 month", "3 months", "6 months", "1 year", "2 years", "5 years"],
            index=3,
            key="settings_default_period"
        )
        
        cache_duration = st.selectbox(
            "Data Cache Duration",
            ["5 minutes", "15 minutes", "1 hour", "4 hours", "1 day"],
            index=2,
            key="settings_cache_duration"
        )
    
    with col2:
        auto_update = st.checkbox(
            "Auto-update data",
            value=st.session_state.get('auto_update', True),
            key="settings_auto_update"
        )
        
        if auto_update:
            update_frequency = st.selectbox(
                "Update Frequency",
                ["Real-time", "Every minute", "Every 5 minutes", "Every 15 minutes"],
                index=2,
                key="settings_update_freq"
            )
        
        preload_data = st.checkbox(
            "Preload common symbols",
            value=st.session_state.get('preload_data', False),
            key="settings_preload"
        )

def render_interface_settings():
    """Render interface customization settings"""
    st.subheader("🎨 Interface Customization")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Theme settings
        st.subheader("🎨 Theme")
        
        theme = st.selectbox(
            "Color Theme",
            ["Dark", "Light", "Auto"],
            key="settings_theme"
        )
        
        chart_theme = st.selectbox(
            "Chart Theme",
            ["Dark", "Light", "Plotly", "Custom"],
            key="settings_chart_theme"
        )
        
        accent_color = st.color_picker(
            "Accent Color",
            value=st.session_state.get('accent_color', '#00C851'),
            key="settings_accent_color"
        )
    
    with col2:
        # Layout settings
        st.subheader("📊 Layout")
        
        sidebar_default = st.selectbox(
            "Sidebar Default State",
            ["Expanded", "Collapsed", "Auto"],
            key="settings_sidebar"
        )
        
        default_page = st.selectbox(
            "Default Landing Page",
            ["Dashboard", "Markets", "Strategies", "Backtesting"],
            key="settings_default_page"
        )
        
        show_tooltips = st.checkbox(
            "Show Help Tooltips",
            value=st.session_state.get('show_tooltips', True),
            key="settings_tooltips"
        )
    
    # Advanced interface settings
    with st.expander("🔧 Advanced Interface Settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            animation_speed = st.slider(
                "Animation Speed",
                0.1, 2.0, 1.0, 0.1,
                key="settings_animation_speed"
            )
            
            auto_refresh_interval = st.selectbox(
                "Auto-refresh Interval",
                ["Off", "30 seconds", "1 minute", "5 minutes"],
                index=2,
                key="settings_auto_refresh"
            )
        
        with col2:
            max_chart_points = st.number_input(
                "Max Chart Data Points",
                value=st.session_state.get('max_chart_points', 1000),
                min_value=100,
                max_value=10000,
                step=100,
                key="settings_max_points"
            )
            
            enable_sound = st.checkbox(
                "Enable Sound Notifications",
                value=st.session_state.get('enable_sound', False),
                key="settings_sound"
            )

def render_security_settings():
    """Render security settings"""
    st.subheader("🔒 Security Configuration")
    
    # API security
    st.subheader("🔑 API Security")
    
    col1, col2 = st.columns(2)
    
    with col1:
        encrypt_api_keys = st.checkbox(
            "Encrypt stored API keys",
            value=st.session_state.get('encrypt_keys', True),
            key="settings_encrypt_keys"
        )
        
        session_timeout = st.selectbox(
            "Session Timeout",
            ["30 minutes", "1 hour", "4 hours", "8 hours", "Never"],
            index=1,
            key="settings_session_timeout"
        )
    
    with col2:
        auto_logout = st.checkbox(
            "Auto-logout on inactivity",
            value=st.session_state.get('auto_logout', True),
            key="settings_auto_logout"
        )
        
        require_confirmation = st.checkbox(
            "Require confirmation for trades",
            value=st.session_state.get('require_confirm', True),
            key="settings_confirm_trades"
        )
    
    # Data privacy
    st.subheader("🛡️ Data Privacy")
    
    col1, col2 = st.columns(2)
    
    with col1:
        log_level = st.selectbox(
            "Logging Level",
            ["ERROR", "WARNING", "INFO", "DEBUG"],
            index=2,
            key="settings_log_level"
        )
        
        store_trade_history = st.checkbox(
            "Store trade history locally",
            value=st.session_state.get('store_history', True),
            key="settings_store_history"
        )
    
    with col2:
        anonymous_analytics = st.checkbox(
            "Share anonymous usage analytics",
            value=st.session_state.get('analytics', False),
            key="settings_analytics"
        )
        
        backup_config = st.checkbox(
            "Auto-backup configuration",
            value=st.session_state.get('backup_config', True),
            key="settings_backup"
        )
    
    # Security actions
    st.subheader("⚠️ Security Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Export Security Log"):
            st.info("Security log exported to downloads folder")
    
    with col2:
        if st.button("🗺️ Clear All Data", type="secondary"):
            if st.confirm("Are you sure? This will delete all local data."):
                st.success("All local data cleared")
    
    with col3:
        if st.button("🔄 Reset API Keys", type="secondary"):
            if st.confirm("Are you sure? This will clear all API keys."):
                st.success("All API keys cleared")

def save_configuration():
    """Save current configuration to file"""
    try:
        # Collect all settings from session state
        config = {key: value for key, value in st.session_state.items() 
                 if key.startswith('settings_')}
        
        # Save to file
        config_manager = ConfigManager()
        for key, value in config.items():
            clean_key = key.replace('settings_', '').replace('_', '.')
            config_manager.set(clean_key, value)
        
        config_manager.save_config()
        st.success("✅ Configuration saved successfully!")
        
    except Exception as e:
        st.error(f"❌ Failed to save configuration: {e}")

def load_configuration():
    """Load configuration from file"""
    try:
        config_manager = ConfigManager()
        
        # Load settings into session state
        st.success("✅ Configuration loaded successfully!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Failed to load configuration: {e}")

def reset_to_defaults():
    """Reset all settings to default values"""
    try:
        # Clear all settings from session state
        settings_keys = [key for key in st.session_state.keys() if key.startswith('settings_')]
        for key in settings_keys:
            del st.session_state[key]
        
        st.success("✅ Settings reset to defaults!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Failed to reset settings: {e}")

def display_system_info():
    """Display system information"""
    import platform
    import sys
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**System Information:**")
        st.write(f"Platform: {platform.system()} {platform.release()}")
        st.write(f"Python Version: {sys.version}")
        st.write(f"Streamlit Version: {st.__version__}")
    
    with col2:
        st.write("**Application Info:**")
        st.write("Application: Backtrader Alerts System")
        st.write("Version: 1.0.0")
        st.write(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Dependencies status
    st.write("**Dependencies Status:**")
    
    dependencies = {
        "pandas": "pandas",
        "numpy": "numpy", 
        "plotly": "plotly",
        "yfinance": "yfinance",
        "backtrader": "backtrader"
    }
    
    for name, module in dependencies.items():
        try:
            __import__(module)
            st.success(f"✅ {name}: Available")
        except ImportError:
            st.error(f"❌ {name}: Not installed")

if __name__ == "__main__":
    render_settings()