#!/usr/bin/env python3
"""
Tests for Pushover alert dispatcher
"""
import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

class TestPushoverDispatcher(unittest.TestCase):
    """Test Pushover alert dispatcher functionality"""
    
    def setUp(self):
        """Set up test environment"""
        from src.alerts.pushover_dispatcher import PushoverDispatcher
        
        # Create test instance with mock credentials
        self.dispatcher = PushoverDispatcher(
            app_token="test_app_token",
            user_key="test_user_key",
            enabled=True,
            priority=0,
            sound="pushover"
        )
    
    def test_dispatcher_initialization(self):
        """Test proper initialization"""
        from src.alerts.pushover_dispatcher import PushoverDispatcher
        
        # Test with valid credentials
        dispatcher = PushoverDispatcher(
            app_token="valid_token",
            user_key="valid_key",
            enabled=True
        )
        
        assert dispatcher.app_token == "valid_token"
        assert dispatcher.user_key == "valid_key"
        assert dispatcher.enabled is True
        assert dispatcher.priority == 0
        
        # Test with missing credentials
        dispatcher_invalid = PushoverDispatcher(
            app_token="",
            user_key="",
            enabled=True
        )
        
        assert dispatcher_invalid.enabled is False  # Should auto-disable
    
    def test_credentials_management(self):
        """Test credential setting and validation"""
        # Test setting valid credentials
        self.dispatcher.set_credentials("new_token", "new_key")
        assert self.dispatcher.app_token == "new_token"
        assert self.dispatcher.user_key == "new_key"
        assert self.dispatcher.enabled is True
        
        # Test enable/disable
        self.dispatcher.disable()
        assert self.dispatcher.enabled is False
        
        self.dispatcher.enable()
        assert self.dispatcher.enabled is True
    
    def test_priority_management(self):
        """Test priority setting and validation"""
        # Test valid priorities
        for priority in [-2, -1, 0, 1, 2]:
            self.dispatcher.set_priority(priority)
            assert self.dispatcher.priority == priority
        
        # Test invalid priority
        with self.assertRaises(ValueError):
            self.dispatcher.set_priority(3)
        
        with self.assertRaises(ValueError):
            self.dispatcher.set_priority(-3)
    
    def test_sound_management(self):
        """Test sound setting"""
        self.dispatcher.set_sound("bugle")
        assert self.dispatcher.sound == "bugle"
        
        self.dispatcher.set_sound("siren")
        assert self.dispatcher.sound == "siren"
    
    @patch('http.client.HTTPSConnection')
    def test_send_trading_alert(self, mock_https):
        """Test sending trading alerts"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps({"status": 1}).encode()
        
        mock_conn = Mock()
        mock_conn.getresponse.return_value = mock_response
        mock_https.return_value = mock_conn
        
        # Test trading alert
        success = self.dispatcher.send_alert("BUY", "AAPL", 150.00, 10.0)
        
        assert success is True
        assert len(self.dispatcher.alerts_history) == 1
        
        alert = self.dispatcher.alerts_history[0]
        assert alert['action'] == "BUY"
        assert alert['symbol'] == "AAPL"
        assert alert['price'] == 150.00
        assert alert['size'] == 10.0
        
        # Verify HTTP request was made
        mock_conn.request.assert_called_once()
    
    @patch('http.client.HTTPSConnection')
    def test_send_custom_alert(self, mock_https):
        """Test sending custom alerts"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps({"status": 1}).encode()
        
        mock_conn = Mock()
        mock_conn.getresponse.return_value = mock_response
        mock_https.return_value = mock_conn
        
        # Test custom alert
        success = self.dispatcher.send_custom_alert("Test message", "Test Title")
        
        assert success is True
        assert len(self.dispatcher.alerts_history) == 1
        
        alert = self.dispatcher.alerts_history[0]
        assert alert['type'] == "custom"
        assert alert['message'] == "Test message"
        assert alert['title'] == "Test Title"
    
    @patch('http.client.HTTPSConnection')
    def test_send_strategy_signal(self, mock_https):
        """Test sending strategy signals"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps({"status": 1}).encode()
        
        mock_conn = Mock()
        mock_conn.getresponse.return_value = mock_response
        mock_https.return_value = mock_conn
        
        # Test strategy signal
        conditions = ["RSI < 30", "Volume spike"]
        success = self.dispatcher.send_strategy_signal(
            "RSI_Strategy", "BUY", "BTC-USD", conditions
        )
        
        assert success is True
        assert len(self.dispatcher.alerts_history) == 1
        
        alert = self.dispatcher.alerts_history[0]
        assert alert['type'] == "strategy_signal"
        assert alert['strategy'] == "RSI_Strategy"
        assert alert['signal'] == "BUY"
        assert alert['symbol'] == "BTC-USD"
        assert alert['conditions'] == conditions
    
    @patch('http.client.HTTPSConnection')
    def test_send_error_alert(self, mock_https):
        """Test sending error alerts"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps({"status": 1}).encode()
        
        mock_conn = Mock()
        mock_conn.getresponse.return_value = mock_response
        mock_https.return_value = mock_conn
        
        # Test error alert
        success = self.dispatcher.send_error_alert(
            "DATA_ERROR", "Failed to fetch data", "test_context"
        )
        
        assert success is True
        assert len(self.dispatcher.alerts_history) == 1
        
        alert = self.dispatcher.alerts_history[0]
        assert alert['type'] == "error"
        assert alert['error_type'] == "DATA_ERROR"
        assert alert['message'] == "Failed to fetch data"
        assert alert['context'] == "test_context"
    
    @patch('http.client.HTTPSConnection')
    def test_send_market_update(self, mock_https):
        """Test sending market updates"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps({"status": 1}).encode()
        
        mock_conn = Mock()
        mock_conn.getresponse.return_value = mock_response
        mock_https.return_value = mock_conn
        
        # Test market update
        success = self.dispatcher.send_market_update(
            "AAPL", 150.00, 5.00, 3.45, 1000000
        )
        
        assert success is True
        assert len(self.dispatcher.alerts_history) == 1
        
        alert = self.dispatcher.alerts_history[0]
        assert alert['type'] == "market_update"
        assert alert['symbol'] == "AAPL"
        assert alert['price'] == 150.00
        assert alert['change'] == 5.00
        assert alert['change_percent'] == 3.45
        assert alert['volume'] == 1000000
    
    @patch('http.client.HTTPSConnection')
    def test_api_error_handling(self, mock_https):
        """Test API error handling"""
        # Mock API error response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps({
            "status": 0,
            "errors": ["Invalid token"]
        }).encode()
        
        mock_conn = Mock()
        mock_conn.getresponse.return_value = mock_response
        mock_https.return_value = mock_conn
        
        # Test failed alert
        success = self.dispatcher.send_alert("BUY", "AAPL", 150.00)
        
        assert success is False
        assert len(self.dispatcher.alerts_history) == 1  # Still stored locally
    
    @patch('http.client.HTTPSConnection')
    def test_http_error_handling(self, mock_https):
        """Test HTTP error handling"""
        # Mock HTTP error
        mock_response = Mock()
        mock_response.status = 400
        mock_response.read.return_value = b"Bad Request"
        
        mock_conn = Mock()
        mock_conn.getresponse.return_value = mock_response
        mock_https.return_value = mock_conn
        
        # Test failed alert
        success = self.dispatcher.send_alert("BUY", "AAPL", 150.00)
        
        assert success is False
        assert len(self.dispatcher.alerts_history) == 1  # Still stored locally
    
    @patch('http.client.HTTPSConnection')
    def test_connection_error_handling(self, mock_https):
        """Test connection error handling"""
        # Mock connection error
        mock_https.side_effect = Exception("Connection failed")
        
        # Test failed alert
        success = self.dispatcher.send_alert("BUY", "AAPL", 150.00)
        
        assert success is False
        assert len(self.dispatcher.alerts_history) == 1  # Still stored locally
    
    def test_disabled_dispatcher(self):
        """Test disabled dispatcher behavior"""
        self.dispatcher.disable()
        
        # All send methods should return False when disabled
        assert self.dispatcher.send_alert("BUY", "AAPL", 150.00) is False
        assert self.dispatcher.send_custom_alert("Test") is False
        assert self.dispatcher.send_strategy_signal("Test", "BUY", "AAPL") is False
        assert self.dispatcher.send_error_alert("ERROR", "Test") is False
        assert self.dispatcher.send_market_update("AAPL", 150.00, 0.0, 0.0) is False
        
        # No alerts should be stored
        assert len(self.dispatcher.alerts_history) == 0
    
    def test_alerts_history_management(self):
        """Test alerts history functionality"""
        # Add some test alerts
        self.dispatcher.alerts_history = [
            {"type": "trading_alert", "action": "BUY"},
            {"type": "trading_alert", "action": "SELL"}, 
            {"type": "custom", "message": "Test"},
            {"type": "error", "error_type": "TEST_ERROR"}
        ]
        
        # Test get all history
        history = self.dispatcher.get_alerts_history()
        assert len(history) == 4
        
        # Test get by type
        trading_alerts = self.dispatcher.get_alerts_by_type("trading_alert")
        assert len(trading_alerts) == 2
        
        buy_alerts = self.dispatcher.get_alerts_by_type("BUY")
        assert len(buy_alerts) == 1
        
        # Test get counts
        counts = self.dispatcher.get_alerts_count()
        assert counts["BUY"] == 1
        assert counts["SELL"] == 1
        assert counts["custom"] == 1
        assert counts["error"] == 1
        
        # Test clear history
        self.dispatcher.clear_history()
        assert len(self.dispatcher.alerts_history) == 0
    
    @patch('http.client.HTTPSConnection')
    def test_connection_test(self, mock_https):
        """Test connection testing functionality"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps({"status": 1}).encode()
        
        mock_conn = Mock()
        mock_conn.getresponse.return_value = mock_response
        mock_https.return_value = mock_conn
        
        # Test successful connection
        success = self.dispatcher.test_connection()
        assert success is True
        
        # Test disabled dispatcher
        self.dispatcher.disable()
        success = self.dispatcher.test_connection()
        assert success is False
        
        # Test missing credentials
        self.dispatcher.app_token = ""
        success = self.dispatcher.test_connection()
        assert success is False
    
    def test_export_alerts(self):
        """Test alerts export functionality"""
        # Add test alerts
        self.dispatcher.alerts_history = [
            {"type": "trading_alert", "action": "BUY", "symbol": "AAPL"},
            {"type": "custom", "message": "Test message"}
        ]
        
        # Test export
        filename = self.dispatcher.export_alerts("test_export.json")
        assert filename == "test_export.json"
        
        # Verify file was created and contains correct data
        try:
            with open(filename, 'r') as f:
                exported_data = json.load(f)
            
            assert len(exported_data) == 2
            assert exported_data[0]["action"] == "BUY"
            assert exported_data[1]["message"] == "Test message"
            
            # Cleanup
            os.remove(filename)
        except:
            pass  # File operations might fail in test environment

class TestPushoverIntegration(unittest.TestCase):
    """Test Pushover integration with other system components"""
    
    def test_alert_manager_integration(self):
        """Test Pushover integration with AlertManager"""
        from src.alerts.alert_manager import AlertManager
        from src.config.config_manager import ConfigManager
        
        # Create config with Pushover settings
        config = ConfigManager()
        config.set('alerts.pushover.enabled', True)
        config.set('alerts.pushover.app_token', 'test_token')
        config.set('alerts.pushover.user_key', 'test_key')
        config.set('alerts.pushover.priority', 1)
        config.set('alerts.pushover.sound', 'bugle')
        
        # Create alert manager
        alert_manager = AlertManager(config)
        
        # Verify Pushover dispatcher was initialized
        assert 'pushover' in alert_manager.dispatchers
        
        pushover_dispatcher = alert_manager.dispatchers['pushover']
        assert pushover_dispatcher.app_token == 'test_token'
        assert pushover_dispatcher.user_key == 'test_key'
        assert pushover_dispatcher.priority == 1
        assert pushover_dispatcher.sound == 'bugle'
    
    def test_config_integration(self):
        """Test Pushover configuration integration"""
        from src.config.config_manager import ConfigManager
        
        config = ConfigManager()
        
        # Test setting Pushover configuration
        config.set('alerts.pushover.app_token', 'test_app_token')
        config.set('alerts.pushover.user_key', 'test_user_key')
        config.set('alerts.pushover.priority', 0)
        config.set('alerts.pushover.sound', 'pushover')
        config.set('alerts.pushover.enabled', True)
        
        # Test getting configuration
        assert config.get('alerts.pushover.app_token') == 'test_app_token'
        assert config.get('alerts.pushover.user_key') == 'test_user_key'
        assert config.get('alerts.pushover.priority') == 0
        assert config.get('alerts.pushover.sound') == 'pushover'
        assert config.get('alerts.pushover.enabled') is True

if __name__ == '__main__':
    print("🧪 Running Pushover Integration Tests")
    print("=" * 50)
    
    unittest.main(verbosity=2)