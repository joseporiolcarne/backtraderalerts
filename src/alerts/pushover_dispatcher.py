"""
Pushover Alert Dispatcher for Backtrader Alerts System
Sends trading alerts via Pushover notifications
"""
import http.client
import urllib.parse
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

class PushoverDispatcher:
    """Pushover-based alert dispatcher for trading notifications"""
    
    def __init__(self, app_token: str = None, user_key: str = None, 
                 enabled: bool = True, priority: int = 0, sound: str = None):
        """
        Initialize Pushover dispatcher
        
        Args:
            app_token: Pushover application token
            user_key: Pushover user key
            enabled: Whether notifications are enabled
            priority: Message priority (-2 to 2)
            sound: Notification sound name
        """
        self.app_token = app_token
        self.user_key = user_key
        self.enabled = enabled
        self.priority = priority
        self.sound = sound
        self.alerts_history = []
        
        # Validate configuration
        if self.enabled and (not self.app_token or not self.user_key):
            print("⚠️ Warning: Pushover enabled but missing app_token or user_key")
            self.enabled = False
    
    def send_alert(self, action: str, symbol: str, price: float, size: float = None,
                   title: str = None, priority: int = None, sound: str = None):
        """
        Send a trading alert via Pushover
        
        Args:
            action: Trading action (BUY/SELL)
            symbol: Trading symbol
            price: Price level
            size: Position size
            title: Custom title for notification
            priority: Override default priority
            sound: Override default sound
        """
        if not self.enabled:
            return False
        
        timestamp = self._get_current_time()
        
        # Format message
        if title is None:
            title = f"🚨 {action} Alert"
        
        message_parts = [
            f"Symbol: {symbol}",
            f"Action: {action}",
            f"Price: ${price:.2f}"
        ]
        
        if size is not None:
            message_parts.append(f"Size: {size:.4f}")
            value = price * size
            message_parts.append(f"Value: ${value:.2f}")
        
        message_parts.append(f"Time: {timestamp}")
        message = "\n".join(message_parts)
        
        # Store in history
        alert_data = {
            "timestamp": timestamp,
            "type": "trading_alert",
            "action": action,
            "symbol": symbol,
            "price": price,
            "size": size,
            "title": title,
            "message": message
        }
        self.alerts_history.append(alert_data)
        
        # Send notification
        return self._send_pushover_message(
            message=message,
            title=title,
            priority=priority or self.priority,
            sound=sound or self.sound
        )
    
    def send_custom_alert(self, message: str, title: str = "Trading Alert", 
                         priority: int = None, sound: str = None):
        """
        Send a custom message via Pushover
        
        Args:
            message: Custom message text
            title: Message title
            priority: Override default priority
            sound: Override default sound
        """
        if not self.enabled:
            return False
        
        timestamp = self._get_current_time()
        
        # Store in history
        alert_data = {
            "timestamp": timestamp,
            "type": "custom",
            "title": title,
            "message": message
        }
        self.alerts_history.append(alert_data)
        
        # Send notification
        return self._send_pushover_message(
            message=message,
            title=title,
            priority=priority or self.priority,
            sound=sound or self.sound
        )
    
    def send_strategy_signal(self, strategy_name: str, signal_type: str, 
                           symbol: str, conditions: List[str] = None,
                           priority: int = None):
        """
        Send strategy signal alert
        
        Args:
            strategy_name: Name of the strategy
            signal_type: Type of signal (BUY/SELL/HOLD)
            symbol: Trading symbol
            conditions: List of conditions that triggered the signal
            priority: Override default priority
        """
        if not self.enabled:
            return False
        
        timestamp = self._get_current_time()
        title = f"📊 {strategy_name} Signal"
        
        message_parts = [
            f"Strategy: {strategy_name}",
            f"Signal: {signal_type}",
            f"Symbol: {symbol}",
            f"Time: {timestamp}"
        ]
        
        if conditions:
            message_parts.append("\nConditions:")
            for condition in conditions:
                message_parts.append(f"• {condition}")
        
        message = "\n".join(message_parts)
        
        # Store in history
        alert_data = {
            "timestamp": timestamp,
            "type": "strategy_signal",
            "strategy": strategy_name,
            "signal": signal_type,
            "symbol": symbol,
            "conditions": conditions or [],
            "title": title,
            "message": message
        }
        self.alerts_history.append(alert_data)
        
        # Send notification
        return self._send_pushover_message(
            message=message,
            title=title,
            priority=priority or self.priority,
            sound=self.sound
        )
    
    def send_error_alert(self, error_type: str, error_message: str, 
                        context: str = None, high_priority: bool = True):
        """
        Send error alert
        
        Args:
            error_type: Type of error
            error_message: Error description
            context: Additional context
            high_priority: Use high priority for errors
        """
        if not self.enabled:
            return False
        
        timestamp = self._get_current_time()
        title = f"🚨 {error_type}"
        
        message_parts = [
            f"Error: {error_message}",
            f"Time: {timestamp}"
        ]
        
        if context:
            message_parts.append(f"Context: {context}")
        
        message = "\n".join(message_parts)
        
        # Store in history
        alert_data = {
            "timestamp": timestamp,
            "type": "error",
            "error_type": error_type,
            "message": error_message,
            "context": context,
            "title": title
        }
        self.alerts_history.append(alert_data)
        
        # Use high priority for errors by default
        priority = 1 if high_priority else (self.priority or 0)
        
        # Send notification
        return self._send_pushover_message(
            message=message,
            title=title,
            priority=priority,
            sound="siren" if high_priority else self.sound
        )
    
    def send_market_update(self, symbol: str, price: float, change: float, 
                          change_percent: float, volume: int = None):
        """
        Send market price update
        
        Args:
            symbol: Trading symbol
            price: Current price
            change: Price change
            change_percent: Percentage change
            volume: Trading volume
        """
        if not self.enabled:
            return False
        
        timestamp = self._get_current_time()
        direction = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        title = f"{direction} {symbol} Update"
        
        message_parts = [
            f"Symbol: {symbol}",
            f"Price: ${price:.2f}",
            f"Change: ${change:+.2f} ({change_percent:+.2f}%)"
        ]
        
        if volume is not None:
            message_parts.append(f"Volume: {volume:,}")
        
        message_parts.append(f"Time: {timestamp}")
        message = "\n".join(message_parts)
        
        # Store in history
        alert_data = {
            "timestamp": timestamp,
            "type": "market_update",
            "symbol": symbol,
            "price": price,
            "change": change,
            "change_percent": change_percent,
            "volume": volume,
            "title": title,
            "message": message
        }
        self.alerts_history.append(alert_data)
        
        # Use low priority for regular market updates
        return self._send_pushover_message(
            message=message,
            title=title,
            priority=-1,  # Low priority
            sound=None  # Silent for regular updates
        )
    
    def _send_pushover_message(self, message: str, title: str = "Trading Alert",
                              priority: int = 0, sound: str = None) -> bool:
        """
        Send message via Pushover API
        
        Args:
            message: Message text
            title: Message title
            priority: Message priority (-2 to 2)
            sound: Notification sound
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.enabled or not self.app_token or not self.user_key:
            return False
        
        try:
            # Prepare request data
            data = {
                "token": self.app_token,
                "user": self.user_key,
                "message": message,
                "title": title,
                "priority": str(priority)
            }
            
            if sound:
                data["sound"] = sound
            
            # Make HTTP request
            conn = http.client.HTTPSConnection("api.pushover.net:443")
            conn.request(
                "POST", 
                "/1/messages.json",
                urllib.parse.urlencode(data),
                {"Content-type": "application/x-www-form-urlencoded"}
            )
            
            response = conn.getresponse()
            response_data = response.read().decode()
            conn.close()
            
            # Check response
            if response.status == 200:
                response_json = json.loads(response_data)
                if response_json.get("status") == 1:
                    return True
                else:
                    print(f"❌ Pushover API error: {response_json.get('errors', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Pushover HTTP error: {response.status} - {response_data}")
                return False
                
        except Exception as e:
            print(f"❌ Pushover connection error: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Test Pushover connection and credentials
        
        Returns:
            bool: True if connection successful
        """
        if not self.enabled:
            print("🔧 Pushover is disabled")
            return False
        
        if not self.app_token or not self.user_key:
            print("❌ Missing Pushover app_token or user_key")
            return False
        
        print("🔧 Testing Pushover connection...")
        success = self._send_pushover_message(
            message="Test message from Backtrader Alerts System",
            title="🧪 Connection Test",
            priority=0
        )
        
        if success:
            print("✅ Pushover connection successful!")
            return True
        else:
            print("❌ Pushover connection failed!")
            return False
    
    def get_alerts_history(self) -> List[Dict[str, Any]]:
        """Get all alerts sent during this session"""
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
        """Clear alerts history"""
        self.alerts_history.clear()
    
    def set_credentials(self, app_token: str, user_key: str):
        """
        Update Pushover credentials
        
        Args:
            app_token: Pushover application token
            user_key: Pushover user key
        """
        self.app_token = app_token
        self.user_key = user_key
        
        # Re-enable if both credentials are provided
        if app_token and user_key:
            self.enabled = True
    
    def set_priority(self, priority: int):
        """
        Set default message priority
        
        Args:
            priority: Priority level (-2 to 2)
        """
        if -2 <= priority <= 2:
            self.priority = priority
        else:
            raise ValueError("Priority must be between -2 and 2")
    
    def set_sound(self, sound: str):
        """
        Set default notification sound
        
        Args:
            sound: Sound name (pushover, bike, bugle, etc.)
        """
        self.sound = sound
    
    def enable(self):
        """Enable Pushover notifications"""
        if self.app_token and self.user_key:
            self.enabled = True
            return True
        else:
            print("❌ Cannot enable: Missing app_token or user_key")
            return False
    
    def disable(self):
        """Disable Pushover notifications"""
        self.enabled = False
    
    def _get_current_time(self) -> str:
        """Get current time as formatted string"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def export_alerts(self, filename: str = None) -> str:
        """
        Export alerts history to JSON file
        
        Args:
            filename: Output filename
            
        Returns:
            str: Filename if successful, None if failed
        """
        if filename is None:
            filename = f"pushover_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.alerts_history, f, indent=2)
            print(f"✅ Pushover alerts exported to {filename}")
            return filename
        except Exception as e:
            print(f"❌ Failed to export Pushover alerts: {e}")
            return None