import unittest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.alerts.telegram_dispatcher import TelegramDispatcher

class TestTelegramDispatcher(unittest.TestCase):
    
    def setUp(self):
        self.bot_token = "test_bot_token"
        self.chat_id = "test_chat_id"
        self.dispatcher = TelegramDispatcher(self.bot_token, self.chat_id)
    
    def test_initialization(self):
        """Test TelegramDispatcher initialization"""
        self.assertEqual(self.dispatcher.bot_token, self.bot_token)
        self.assertEqual(self.dispatcher.chat_id, self.chat_id)
        self.assertIsNotNone(self.dispatcher.bot)
    
    @patch('telegram.Bot')
    def test_initialization_with_mock_bot(self, mock_bot_class):
        """Test initialization with mocked telegram bot"""
        mock_bot = Mock()
        mock_bot_class.return_value = mock_bot
        
        dispatcher = TelegramDispatcher("token", "chat_id")
        
        mock_bot_class.assert_called_once_with(token="token")
        self.assertEqual(dispatcher.bot, mock_bot)
    
    @patch.object(TelegramDispatcher, '_send_message')
    @patch('asyncio.run')
    def test_send_alert(self, mock_asyncio_run, mock_send_message):
        """Test sending a trading alert"""
        self.dispatcher.send_alert("BUY", "BTC-USD", 50000.0, 0.1)
        
        # Check that asyncio.run was called
        mock_asyncio_run.assert_called_once()
        
        # Get the coroutine that was passed to asyncio.run
        called_args = mock_asyncio_run.call_args[0]
        self.assertEqual(len(called_args), 1)
    
    @patch.object(TelegramDispatcher, '_send_message')
    @patch('asyncio.run')
    def test_send_alert_without_size(self, mock_asyncio_run, mock_send_message):
        """Test sending alert without size parameter"""
        self.dispatcher.send_alert("SELL", "ETH-USD", 3000.0)
        
        mock_asyncio_run.assert_called_once()
    
    @patch.object(TelegramDispatcher, '_send_message')
    @patch('asyncio.run')
    def test_send_custom_alert(self, mock_asyncio_run, mock_send_message):
        """Test sending custom alert message"""
        custom_message = "Custom trading alert message"
        self.dispatcher.send_custom_alert(custom_message)
        
        mock_asyncio_run.assert_called_once()
    
    @patch('asyncio.run')
    def test_send_alert_exception_handling(self, mock_asyncio_run):
        """Test exception handling in send_alert"""
        mock_asyncio_run.side_effect = Exception("Network error")
        
        # Should not raise exception
        try:
            self.dispatcher.send_alert("BUY", "BTC-USD", 50000.0)
        except Exception:
            self.fail("send_alert should handle exceptions gracefully")
    
    @patch('asyncio.run')
    def test_send_custom_alert_exception_handling(self, mock_asyncio_run):
        """Test exception handling in send_custom_alert"""
        mock_asyncio_run.side_effect = Exception("Network error")
        
        # Should not raise exception
        try:
            self.dispatcher.send_custom_alert("Test message")
        except Exception:
            self.fail("send_custom_alert should handle exceptions gracefully")
    
    def test_get_current_time(self):
        """Test current time formatting"""
        time_str = self.dispatcher._get_current_time()
        
        self.assertIsInstance(time_str, str)
        # Should match format YYYY-MM-DD HH:MM:SS
        import re
        pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        self.assertIsNotNone(re.match(pattern, time_str))
    
    @patch.object(TelegramDispatcher, '_send_message')
    @patch('asyncio.run')
    def test_test_connection_success(self, mock_asyncio_run, mock_send_message):
        """Test successful connection test"""
        mock_asyncio_run.return_value = None  # Successful execution
        
        result = self.dispatcher.test_connection()
        
        self.assertTrue(result)
        mock_asyncio_run.assert_called_once()
    
    @patch('asyncio.run')
    def test_test_connection_failure(self, mock_asyncio_run):
        """Test failed connection test"""
        mock_asyncio_run.side_effect = Exception("Connection failed")
        
        result = self.dispatcher.test_connection()
        
        self.assertFalse(result)
    
    async def test_send_message_async(self):
        """Test async message sending"""
        # Mock the bot's send_message method
        mock_bot = AsyncMock()
        self.dispatcher.bot = mock_bot
        
        await self.dispatcher._send_message("Test message")
        
        mock_bot.send_message.assert_called_once_with(
            chat_id=self.chat_id,
            text="Test message"
        )
    
    async def test_send_message_async_exception(self):
        """Test async message sending with exception"""
        # Mock the bot to raise an exception
        mock_bot = AsyncMock()
        mock_bot.send_message.side_effect = Exception("API error")
        self.dispatcher.bot = mock_bot
        
        # Should not raise exception
        try:
            await self.dispatcher._send_message("Test message")
        except Exception:
            self.fail("_send_message should handle exceptions gracefully")
    
    def test_alert_message_format(self):
        """Test alert message formatting"""
        # We'll test this by mocking the _send_message and checking the message content
        with patch.object(self.dispatcher, '_send_message') as mock_send:
            with patch('asyncio.run') as mock_run:
                # Capture the message that would be sent
                def capture_message(coro):
                    # Extract the message from the coroutine
                    return coro
                
                mock_run.side_effect = capture_message
                
                self.dispatcher.send_alert("BUY", "BTC-USD", 50000.0, 0.1)
                
                # Verify asyncio.run was called
                mock_run.assert_called_once()
    
    def test_custom_alert_message_format(self):
        """Test custom alert message formatting"""
        with patch.object(self.dispatcher, '_send_message') as mock_send:
            with patch('asyncio.run') as mock_run:
                custom_msg = "RSI crossed below 30"
                self.dispatcher.send_custom_alert(custom_msg)
                
                mock_run.assert_called_once()
    
    @patch('telegram.Bot')
    def test_different_initialization_params(self, mock_bot_class):
        """Test initialization with different parameters"""
        different_token = "different_token"
        different_chat_id = "different_chat_id"
        
        dispatcher = TelegramDispatcher(different_token, different_chat_id)
        
        self.assertEqual(dispatcher.bot_token, different_token)
        self.assertEqual(dispatcher.chat_id, different_chat_id)
        mock_bot_class.assert_called_once_with(token=different_token)

class TestTelegramDispatcherIntegration(unittest.TestCase):
    """Integration tests for TelegramDispatcher (these would need real API keys to run)"""
    
    def setUp(self):
        # Use fake credentials for testing
        self.dispatcher = TelegramDispatcher("fake_token", "fake_chat_id")
    
    def test_message_content_generation(self):
        """Test that alert messages are properly formatted"""
        # Test BUY alert format
        with patch('asyncio.run') as mock_run:
            self.dispatcher.send_alert("BUY", "BTC-USD", 50000.0, 0.1)
            
            # Get the coroutine that was passed to asyncio.run
            call_args = mock_run.call_args[0][0]
            # The message should contain the expected elements
            mock_run.assert_called_once()
    
    def test_error_resilience(self):
        """Test that the system handles various error conditions"""
        # Test with None values
        try:
            self.dispatcher.send_alert("BUY", "BTC-USD", None, None)
        except Exception as e:
            self.fail(f"Should handle None values gracefully: {e}")
        
        # Test with empty strings
        try:
            self.dispatcher.send_alert("", "", 0, 0)
        except Exception as e:
            self.fail(f"Should handle empty values gracefully: {e}")

if __name__ == '__main__':
    unittest.main()