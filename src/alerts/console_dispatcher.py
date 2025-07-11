from datetime import datetime
from typing import Optional, List
import json

class ConsoleDispatcher:
    """Console-based alert dispatcher for testing and development"""
    
    def __init__(self, log_to_file: bool = False, log_file: str = "alerts.log"):
        self.log_to_file = log_to_file
        self.log_file = log_file
        self.alerts_history = []
    
    def send_alert(self, action: str, symbol: str, price: float, size: float = None):
        """Send a trading alert to console"""
        timestamp = self._get_current_time()
        
        # Format the message
        message = f"🚨 {action} ALERT 🚨"
        details = {
            "timestamp": timestamp,
            "action": action,
            "symbol": symbol,
            "price": price,
            "size": size
        }
        
        # Store in history
        self.alerts_history.append(details)
        
        # Print to console
        print("\n" + "="*50)
        print(message)
        print(f"Time: {timestamp}")
        print(f"Symbol: {symbol}")
        print(f"Price: ${price:.2f}")
        if size is not None:
            print(f"Size: {size:.4f}")
        print("="*50)
        
        # Log to file if enabled
        if self.log_to_file:
            self._log_to_file(details)
    
    def send_custom_alert(self, message: str):
        """Send a custom message to console"""
        timestamp = self._get_current_time()
        
        details = {
            "timestamp": timestamp,
            "type": "custom",
            "message": message
        }
        
        # Store in history
        self.alerts_history.append(details)
        
        # Print to console
        print("\n" + "-"*50)
        print(f"🤖 Alert - {timestamp}")
        print(message)
        print("-"*50)
        
        # Log to file if enabled
        if self.log_to_file:
            self._log_to_file(details)
    
    def send_strategy_signal(self, strategy_name: str, signal_type: str, 
                           symbol: str, conditions: List[str] = None):
        """Send strategy signal alert"""
        timestamp = self._get_current_time()
        
        details = {
            "timestamp": timestamp,
            "type": "strategy_signal",
            "strategy": strategy_name,
            "signal": signal_type,
            "symbol": symbol,
            "conditions": conditions or []
        }
        
        # Store in history
        self.alerts_history.append(details)
        
        # Print to console
        print("\n" + "⚡"*25)
        print(f"📊 STRATEGY SIGNAL - {timestamp}")
        print(f"Strategy: {strategy_name}")
        print(f"Signal: {signal_type}")
        print(f"Symbol: {symbol}")
        if conditions:
            print("Triggered conditions:")
            for condition in conditions:
                print(f"  ✓ {condition}")
        print("⚡"*25)
        
        # Log to file if enabled
        if self.log_to_file:
            self._log_to_file(details)
    
    def send_error_alert(self, error_type: str, error_message: str, context: str = None):
        """Send error alert"""
        timestamp = self._get_current_time()
        
        details = {
            "timestamp": timestamp,
            "type": "error",
            "error_type": error_type,
            "message": error_message,
            "context": context
        }
        
        # Store in history
        self.alerts_history.append(details)
        
        # Print to console
        print("\n" + "❌"*25)
        print(f"🚨 ERROR ALERT - {timestamp}")
        print(f"Type: {error_type}")
        print(f"Message: {error_message}")
        if context:
            print(f"Context: {context}")
        print("❌"*25)
        
        # Log to file if enabled
        if self.log_to_file:
            self._log_to_file(details)
    
    def get_alerts_history(self) -> List[dict]:
        """Get all alerts sent during this session"""
        return self.alerts_history.copy()
    
    def get_alerts_by_type(self, alert_type: str) -> List[dict]:
        """Get alerts filtered by type"""
        return [alert for alert in self.alerts_history 
                if alert.get('type') == alert_type or alert.get('action') == alert_type]
    
    def get_alerts_count(self) -> dict:
        """Get count of alerts by type"""
        counts = {}
        for alert in self.alerts_history:
            alert_type = alert.get('action') or alert.get('type', 'unknown')
            counts[alert_type] = counts.get(alert_type, 0) + 1
        return counts
    
    def clear_history(self):
        """Clear alerts history"""
        self.alerts_history.clear()
    
    def test_connection(self) -> bool:
        """Test connection (always returns True for console)"""
        print("🔧 Console Dispatcher Test")
        print("Connection successful! ✅")
        return True
    
    def _get_current_time(self) -> str:
        """Get current time as formatted string"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _log_to_file(self, details: dict):
        """Log alert details to file"""
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(details) + '\n')
        except Exception as e:
            print(f"Warning: Could not write to log file: {e}")
    
    def export_alerts(self, filename: str = None) -> str:
        """Export alerts history to JSON file"""
        if filename is None:
            filename = f"alerts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.alerts_history, f, indent=2)
            print(f"✅ Alerts exported to {filename}")
            return filename
        except Exception as e:
            print(f"❌ Failed to export alerts: {e}")
            return None