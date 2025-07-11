import asyncio
from typing import Optional

try:
    import telegram
except ImportError:
    telegram = None

class TelegramDispatcher:
    def __init__(self, bot_token: str, chat_id: str):
        if telegram is None:
            raise ImportError("python-telegram-bot not installed. Install with: pip install python-telegram-bot")
        
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot = telegram.Bot(token=bot_token)
    
    def send_alert(self, action: str, symbol: str, price: float, size: float = None):
        """Send a trading alert via Telegram"""
        try:
            # Format the message
            message = f"🚨 {action} ALERT 🚨\n\n"
            message += f"Symbol: {symbol}\n"
            message += f"Price: ${price:.2f}\n"
            
            if size is not None:
                message += f"Size: {size:.4f}\n"
            
            message += f"\n⏰ Time: {self._get_current_time()}"
            
            # Send the message
            asyncio.run(self._send_message(message))
            
        except Exception as e:
            print(f"Error sending Telegram alert: {e}")
    
    def send_custom_alert(self, message: str):
        """Send a custom message via Telegram"""
        try:
            formatted_message = f"🤖 Backtrader Alert\n\n{message}\n\n⏰ {self._get_current_time()}"
            asyncio.run(self._send_message(formatted_message))
        except Exception as e:
            print(f"Error sending custom Telegram alert: {e}")
    
    async def _send_message(self, message: str):
        """Send message asynchronously"""
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message)
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")
    
    def _get_current_time(self) -> str:
        """Get current time as formatted string"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def test_connection(self) -> bool:
        """Test if the bot can send messages"""
        try:
            test_message = "🔧 Backtrader Alerts Test\n\nConnection successful! ✅"
            asyncio.run(self._send_message(test_message))
            return True
        except Exception as e:
            print(f"Telegram connection test failed: {e}")
            return False