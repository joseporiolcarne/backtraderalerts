"""
Alert Manager for coordinating multiple notification systems
Supports Telegram, Pushover, and Console alerts
"""
from typing import List, Dict, Any, Optional
from datetime import datetime

class AlertManager:
    """
    Manages multiple alert dispatchers (Telegram, Pushover, Console)
    Provides unified interface for sending alerts across all enabled systems
    """
    
    def __init__(self, config_manager=None):
        """
        Initialize alert manager with configuration
        
        Args:
            config_manager: ConfigManager instance for loading alert settings
        """
        self.dispatchers = {}
        self.config = config_manager
        self.alerts_history = []
        
        # Initialize dispatchers based on configuration
        if config_manager:
            self._initialize_dispatchers()
    
    def _initialize_dispatchers(self):
        """Initialize alert dispatchers based on configuration"""
        if not self.config:
            return
        
        # Initialize Console Dispatcher
        console_config = self.config.get('alerts.console', {})
        if console_config.get('enabled', True):
            try:
                from .console_dispatcher import ConsoleDispatcher
                self.dispatchers['console'] = ConsoleDispatcher(
                    log_to_file=console_config.get('log_to_file', False)
                )
                print("✅ Console alerts initialized")
            except ImportError as e:
                print(f"⚠️ Could not initialize Console dispatcher: {e}")
        
        # Initialize Telegram Dispatcher
        telegram_config = self.config.get('alerts.telegram', {})
        if telegram_config.get('enabled', False):
            try:
                from .telegram_dispatcher import TelegramDispatcher
                bot_token = telegram_config.get('bot_token')
                chat_id = telegram_config.get('chat_id')
                
                if bot_token and chat_id:
                    self.dispatchers['telegram'] = TelegramDispatcher(bot_token, chat_id)
                    print("✅ Telegram alerts initialized")
                else:
                    print("⚠️ Telegram enabled but missing bot_token or chat_id")
            except ImportError as e:
                print(f"⚠️ Could not initialize Telegram dispatcher: {e}")
        
        # Initialize Pushover Dispatcher
        pushover_config = self.config.get('alerts.pushover', {})
        if pushover_config.get('enabled', False):
            try:
                from .pushover_dispatcher import PushoverDispatcher
                app_token = pushover_config.get('app_token')
                user_key = pushover_config.get('user_key')
                priority = pushover_config.get('priority', 0)
                sound = pushover_config.get('sound', '')
                
                if app_token and user_key:
                    self.dispatchers['pushover'] = PushoverDispatcher(
                        app_token=app_token,
                        user_key=user_key,
                        priority=priority,
                        sound=sound if sound else None
                    )
                    print("✅ Pushover alerts initialized")
                else:
                    print("⚠️ Pushover enabled but missing app_token or user_key")
            except ImportError as e:
                print(f"⚠️ Could not initialize Pushover dispatcher: {e}")
    
    def add_dispatcher(self, name: str, dispatcher):
        """
        Add a custom alert dispatcher
        
        Args:
            name: Unique name for the dispatcher
            dispatcher: Alert dispatcher instance
        """
        self.dispatchers[name] = dispatcher
        print(f"✅ Added {name} dispatcher")
    
    def remove_dispatcher(self, name: str):
        """
        Remove an alert dispatcher
        
        Args:
            name: Name of dispatcher to remove
        """
        if name in self.dispatchers:
            del self.dispatchers[name]
            print(f"🗑️ Removed {name} dispatcher")
    
    def send_alert(self, action: str, symbol: str, price: float, size: float = None,
                   dispatchers: List[str] = None):
        """
        Send trading alert to all enabled dispatchers
        
        Args:
            action: Trading action (BUY/SELL)
            symbol: Trading symbol
            price: Price level
            size: Position size
            dispatchers: Specific dispatchers to use (None = all)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Store in central history
        alert_data = {
            "timestamp": timestamp,
            "type": "trading_alert",
            "action": action,
            "symbol": symbol,
            "price": price,
            "size": size
        }
        self.alerts_history.append(alert_data)
        
        # Send to all enabled dispatchers
        target_dispatchers = dispatchers or list(self.dispatchers.keys())
        results = {}
        
        for name in target_dispatchers:
            if name in self.dispatchers:
                try:
                    dispatcher = self.dispatchers[name]
                    success = dispatcher.send_alert(action, symbol, price, size)
                    results[name] = success
                except Exception as e:
                    print(f"❌ Error sending alert via {name}: {e}")
                    results[name] = False
        
        return results
    
    def send_custom_alert(self, message: str, title: str = "Trading Alert",
                         dispatchers: List[str] = None):
        """
        Send custom message to all enabled dispatchers
        
        Args:
            message: Custom message text
            title: Message title
            dispatchers: Specific dispatchers to use (None = all)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Store in central history
        alert_data = {
            "timestamp": timestamp,
            "type": "custom",
            "title": title,
            "message": message
        }
        self.alerts_history.append(alert_data)
        
        # Send to all enabled dispatchers
        target_dispatchers = dispatchers or list(self.dispatchers.keys())
        results = {}
        
        for name in target_dispatchers:
            if name in self.dispatchers:
                try:
                    dispatcher = self.dispatchers[name]
                    if hasattr(dispatcher, 'send_custom_alert'):
                        success = dispatcher.send_custom_alert(message, title)
                    else:
                        # Fallback for dispatchers without custom alert method
                        success = dispatcher.send_alert("INFO", "CUSTOM", 0.0)
                    results[name] = success
                except Exception as e:
                    print(f"❌ Error sending custom alert via {name}: {e}")
                    results[name] = False
        
        return results
    
    def send_strategy_signal(self, strategy_name: str, signal_type: str, 
                           symbol: str, conditions: List[str] = None,
                           dispatchers: List[str] = None):
        """
        Send strategy signal to all enabled dispatchers
        
        Args:
            strategy_name: Name of the strategy
            signal_type: Type of signal (BUY/SELL/HOLD)
            symbol: Trading symbol
            conditions: List of conditions that triggered the signal
            dispatchers: Specific dispatchers to use (None = all)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Store in central history
        alert_data = {
            "timestamp": timestamp,
            "type": "strategy_signal",
            "strategy": strategy_name,
            "signal": signal_type,
            "symbol": symbol,
            "conditions": conditions or []
        }
        self.alerts_history.append(alert_data)
        
        # Send to all enabled dispatchers
        target_dispatchers = dispatchers or list(self.dispatchers.keys())
        results = {}
        
        for name in target_dispatchers:
            if name in self.dispatchers:
                try:
                    dispatcher = self.dispatchers[name]
                    if hasattr(dispatcher, 'send_strategy_signal'):
                        success = dispatcher.send_strategy_signal(
                            strategy_name, signal_type, symbol, conditions
                        )
                    else:
                        # Fallback for dispatchers without strategy signal method
                        message = f"{strategy_name}: {signal_type} {symbol}"
                        success = dispatcher.send_custom_alert(message, "Strategy Signal")
                    results[name] = success
                except Exception as e:
                    print(f"❌ Error sending strategy signal via {name}: {e}")
                    results[name] = False
        
        return results
    
    def send_error_alert(self, error_type: str, error_message: str, 
                        context: str = None, dispatchers: List[str] = None):
        """
        Send error alert to all enabled dispatchers
        
        Args:
            error_type: Type of error
            error_message: Error description
            context: Additional context
            dispatchers: Specific dispatchers to use (None = all)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Store in central history
        alert_data = {
            "timestamp": timestamp,
            "type": "error",
            "error_type": error_type,
            "message": error_message,
            "context": context
        }
        self.alerts_history.append(alert_data)
        
        # Send to all enabled dispatchers
        target_dispatchers = dispatchers or list(self.dispatchers.keys())
        results = {}
        
        for name in target_dispatchers:
            if name in self.dispatchers:
                try:
                    dispatcher = self.dispatchers[name]
                    if hasattr(dispatcher, 'send_error_alert'):
                        success = dispatcher.send_error_alert(error_type, error_message, context)
                    else:
                        # Fallback for dispatchers without error alert method
                        message = f"Error: {error_message}"
                        success = dispatcher.send_custom_alert(message, f"🚨 {error_type}")
                    results[name] = success
                except Exception as e:
                    print(f"❌ Error sending error alert via {name}: {e}")
                    results[name] = False
        
        return results
    
    def send_market_update(self, symbol: str, price: float, change: float, 
                          change_percent: float, volume: int = None,
                          dispatchers: List[str] = None):
        """
        Send market update (only to dispatchers that support it)
        
        Args:
            symbol: Trading symbol
            price: Current price
            change: Price change
            change_percent: Percentage change
            volume: Trading volume
            dispatchers: Specific dispatchers to use (None = all)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Store in central history
        alert_data = {
            "timestamp": timestamp,
            "type": "market_update",
            "symbol": symbol,
            "price": price,
            "change": change,
            "change_percent": change_percent,
            "volume": volume
        }
        self.alerts_history.append(alert_data)
        
        # Send to dispatchers that support market updates
        target_dispatchers = dispatchers or list(self.dispatchers.keys())
        results = {}
        
        for name in target_dispatchers:
            if name in self.dispatchers:
                try:
                    dispatcher = self.dispatchers[name]
                    if hasattr(dispatcher, 'send_market_update'):
                        success = dispatcher.send_market_update(
                            symbol, price, change, change_percent, volume
                        )
                        results[name] = success
                    else:
                        # Skip dispatchers that don't support market updates
                        results[name] = "skipped"
                except Exception as e:
                    print(f"❌ Error sending market update via {name}: {e}")
                    results[name] = False
        
        return results
    
    def test_all_connections(self) -> Dict[str, bool]:
        """
        Test connection for all enabled dispatchers
        
        Returns:
            Dict mapping dispatcher names to connection success status
        """
        results = {}
        
        for name, dispatcher in self.dispatchers.items():
            try:
                if hasattr(dispatcher, 'test_connection'):
                    success = dispatcher.test_connection()
                    results[name] = success
                else:
                    # For dispatchers without test_connection, assume working
                    results[name] = True
            except Exception as e:
                print(f"❌ Error testing {name} connection: {e}")
                results[name] = False
        
        return results
    
    def get_active_dispatchers(self) -> List[str]:
        """Get list of active dispatcher names"""
        return list(self.dispatchers.keys())
    
    def get_alerts_history(self) -> List[Dict[str, Any]]:
        """Get all alerts from central history"""
        return self.alerts_history.copy()
    
    def get_alerts_by_type(self, alert_type: str) -> List[Dict[str, Any]]:
        """Get alerts filtered by type"""
        return [alert for alert in self.alerts_history 
                if alert.get('type') == alert_type or alert.get('action') == alert_type]
    
    def get_alerts_count(self) -> Dict[str, int]:
        """Get count of alerts by type"""
        counts = {}
        for alert in self.alerts_history:
            alert_type = alert.get('action') or alert.get('type', 'unknown')
            counts[alert_type] = counts.get(alert_type, 0) + 1
        return counts
    
    def clear_history(self):
        """Clear central alerts history"""
        self.alerts_history.clear()
        
        # Also clear individual dispatcher histories
        for dispatcher in self.dispatchers.values():
            if hasattr(dispatcher, 'clear_history'):
                dispatcher.clear_history()
    
    def get_dispatcher_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for each dispatcher"""
        stats = {}
        
        for name, dispatcher in self.dispatchers.items():
            dispatcher_stats = {
                "enabled": True,
                "type": dispatcher.__class__.__name__,
                "alerts_sent": 0
            }
            
            # Get dispatcher-specific stats if available
            if hasattr(dispatcher, 'get_alerts_count'):
                dispatcher_stats["alerts_sent"] = sum(dispatcher.get_alerts_count().values())
            
            if hasattr(dispatcher, 'enabled'):
                dispatcher_stats["enabled"] = dispatcher.enabled
            
            stats[name] = dispatcher_stats
        
        return stats
    
    def export_all_alerts(self, filename: str = None) -> str:
        """
        Export all alerts from all dispatchers
        
        Args:
            filename: Output filename
            
        Returns:
            str: Filename if successful, None if failed
        """
        if filename is None:
            filename = f"all_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            import json
            
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "central_history": self.alerts_history,
                "dispatcher_histories": {}
            }
            
            # Collect histories from all dispatchers
            for name, dispatcher in self.dispatchers.items():
                if hasattr(dispatcher, 'get_alerts_history'):
                    export_data["dispatcher_histories"][name] = dispatcher.get_alerts_history()
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"✅ All alerts exported to {filename}")
            return filename
        except Exception as e:
            print(f"❌ Failed to export all alerts: {e}")
            return None