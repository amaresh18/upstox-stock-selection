"""
Telegram notification utility for sending alerts.

This module provides functions to send Telegram notifications when stock alerts are detected.
"""

import os
import asyncio
import aiohttp
from typing import Dict, List, Optional
from datetime import datetime


class TelegramNotifier:
    """Telegram notification sender."""
    
    def __init__(self, bot_token: str = None, chat_id: str = None):
        """
        Initialize Telegram notifier.
        
        Args:
            bot_token: Telegram bot token (from @BotFather)
            chat_id: Telegram chat ID (user or group)
        """
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        self.enabled = bool(self.bot_token and self.chat_id)
        
        if not self.enabled:
            print("⚠️  Telegram notifications disabled (TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set)")
    
    def format_alert_message(self, alert: Dict) -> str:
        """
        Format a single alert as a Telegram message.
        
        Args:
            alert: Alert dictionary with symbol, signal_type, price, etc.
            
        Returns:
            Formatted message string
        """
        symbol = alert.get('symbol', 'N/A')
        signal_type = alert.get('signal_type', 'N/A')
        price = alert.get('price', 0)
        vol_ratio = alert.get('vol_ratio', 0)
        swing_high = alert.get('swing_high', 0)
        swing_low = alert.get('swing_low', 0)
        timestamp = alert.get('timestamp', 'N/A')
        
        # Format timestamp
        if isinstance(timestamp, str):
            try:
                ts = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                timestamp_str = ts.strftime('%Y-%m-%d %H:%M:%S')
            except:
                timestamp_str = str(timestamp)
        else:
            timestamp_str = str(timestamp)
        
        # Determine level and direction
        if signal_type == 'BREAKOUT':
            emoji = "🟢"
            level = swing_high
            direction = "ABOVE"
            signal_text = "BREAKOUT"
        else:
            emoji = "🔴"
            level = swing_low
            direction = "BELOW"
            signal_text = "BREAKDOWN"
        
        # Format message
        message = f"{emoji} *{signal_text}* - {symbol}\n\n"
        message += f"⏰ Time: `{timestamp_str}`\n"
        message += f"💰 Price: ₹{price:.2f}\n"
        message += f"📊 Level: ₹{level:.2f} ({direction})\n"
        message += f"📈 Volume: {vol_ratio:.2f}x average\n"
        
        return message
    
    async def send_message(self, message: str, parse_mode: str = "Markdown") -> bool:
        """
        Send a message to Telegram.
        
        Args:
            message: Message text
            parse_mode: Parse mode (Markdown, HTML, or None)
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        return True
                    else:
                        error_text = await response.text()
                        print(f"⚠️  Telegram API error: Status {response.status}, {error_text[:200]}")
                        return False
                        
        except Exception as e:
            print(f"⚠️  Error sending Telegram message: {e}")
            return False
    
    async def send_alert(self, alert: Dict) -> bool:
        """
        Send a single alert to Telegram.
        
        Args:
            alert: Alert dictionary
            
        Returns:
            True if sent successfully, False otherwise
        """
        message = self.format_alert_message(alert)
        return await self.send_message(message)
    
    async def send_alerts_batch(self, alerts: List[Dict], max_alerts: int = 10) -> int:
        """
        Send multiple alerts to Telegram.
        If there are many alerts, sends a summary first.
        
        Args:
            alerts: List of alert dictionaries
            max_alerts: Maximum number of individual alerts to send (rest will be summarized)
            
        Returns:
            Number of alerts sent successfully
        """
        if not self.enabled or not alerts:
            return 0
        
        sent_count = 0
        
        # If too many alerts, send summary first
        if len(alerts) > max_alerts:
            summary = f"🔔 *{len(alerts)} New Alerts Detected!*\n\n"
            summary += f"Showing first {max_alerts} alerts:\n\n"
            await self.send_message(summary)
            
            # Send first max_alerts individually
            for alert in alerts[:max_alerts]:
                if await self.send_alert(alert):
                    sent_count += 1
                await asyncio.sleep(0.1)  # Small delay to avoid rate limiting
            
            # Send summary of remaining
            remaining = len(alerts) - max_alerts
            if remaining > 0:
                summary_msg = f"\n... and {remaining} more alerts. Check CSV file for details."
                await self.send_message(summary_msg)
        else:
            # Send all alerts individually
            for alert in alerts:
                if await self.send_alert(alert):
                    sent_count += 1
                await asyncio.sleep(0.1)  # Small delay to avoid rate limiting
        
        return sent_count

