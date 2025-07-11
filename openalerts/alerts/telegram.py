import requests
import asyncio
import aiohttp
from typing import List, Optional
from datetime import datetime
import time


class TelegramDispatcher:
    def __init__(self, bot_token: str, chat_id: str, rate_limit: int = 30):
        """
        Initialize Telegram dispatcher
        
        Args:
            bot_token: Telegram bot token
            chat_id: Chat ID to send messages to
            rate_limit: Minimum seconds between messages
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.rate_limit = rate_limit
        self.last_message_time = 0
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
    def send_message(self, message: str, parse_mode: str = "Markdown") -> bool:
        """Send a single message to Telegram"""
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_message_time
        if time_since_last < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last)
        
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": parse_mode
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            self.last_message_time = time.time()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error sending Telegram message: {e}")
            return False
    
    def send_batch(self, messages: List[str]) -> List[bool]:
        """Send multiple messages with rate limiting"""
        results = []
        for msg in messages:
            result = self.send_message(msg)
            results.append(result)
        return results
    
    def format_alert(self, alert_type: str, symbol: str, data: dict) -> str:
        """Format alert message for better readability"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"🚨 *{alert_type} Alert*\n"
        message += f"Symbol: `{symbol}`\n"
        message += f"Time: {timestamp}\n"
        message += "─" * 20 + "\n"
        
        for key, value in data.items():
            if isinstance(value, float):
                message += f"{key}: `{value:.4f}`\n"
            else:
                message += f"{key}: `{value}`\n"
        
        return message


async def send_telegram_async(message: str, chat_id: str, token: str) -> bool:
    """Async version for high-frequency alerts"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, timeout=10) as response:
                return response.status == 200
        except Exception as e:
            print(f"Async Telegram error: {e}")
            return False


def send_telegram(message: str, chat_id: str, token: str) -> bool:
    """Simple synchronous function for basic usage"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram error: {e}")
        return False


class AlertQueue:
    """Queue system for managing alerts"""
    def __init__(self, dispatcher: TelegramDispatcher):
        self.dispatcher = dispatcher
        self.queue: List[str] = []
        self.is_processing = False
        
    def add_alert(self, message: str):
        """Add alert to queue"""
        self.queue.append(message)
        
    async def process_queue(self):
        """Process all queued alerts"""
        if self.is_processing:
            return
            
        self.is_processing = True
        while self.queue:
            message = self.queue.pop(0)
            self.dispatcher.send_message(message)
        self.is_processing = False
        
    def get_queue_size(self) -> int:
        """Get number of pending alerts"""
        return len(self.queue)