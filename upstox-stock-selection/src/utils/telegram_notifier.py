"""
Telegram notification utility for sending alerts.

This module provides functions to send Telegram notifications when stock alerts are detected.
"""

import os
import asyncio
import aiohttp
import pandas as pd
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
            alert: Alert dictionary with symbol, signal_type/pattern_type, price, etc.
            
        Returns:
            Formatted message string
        """
        symbol = alert.get('symbol', 'N/A')
        signal_type = alert.get('signal_type', alert.get('pattern_type', 'N/A'))
        price = alert.get('price', 0)
        timestamp = alert.get('timestamp', 'N/A')
        
        # Format timestamp
        if isinstance(timestamp, str):
            try:
                ts = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                timestamp_str = ts.strftime('%Y-%m-%d %H:%M:%S')
            except:
                try:
                    # Try parsing as datetime string
                    ts = pd.to_datetime(timestamp)
                    timestamp_str = ts.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    timestamp_str = str(timestamp)
        else:
            timestamp_str = str(timestamp)
        
        # Handle pattern-based alerts
        if signal_type in ['RSI_BULLISH_DIVERGENCE', 'RSI_BEARISH_DIVERGENCE', 
                          'UPTREND_RETEST', 'DOWNTREND_RETEST']:
            return self._format_pattern_alert(alert, signal_type, symbol, price, timestamp_str)
        
        # Handle traditional breakout/breakdown alerts
        vol_ratio = alert.get('vol_ratio', 0)
        swing_high = alert.get('swing_high', 0)
        swing_low = alert.get('swing_low', 0)
        
        # Determine level and direction
        if signal_type == 'BREAKOUT':
            emoji = "🟢"
            level = swing_high
            direction = "ABOVE"
            signal_text = "BREAKOUT"
        elif signal_type == 'BREAKDOWN':
            emoji = "🔴"
            level = swing_low
            direction = "BELOW"
            signal_text = "BREAKDOWN"
        elif signal_type == 'VOLUME_SPIKE_15M':
            emoji = "📊"
            signal_text = "VOLUME SPIKE (15M)"
            message = f"{emoji} *{signal_text}* - {symbol}\n\n"
            message += f"⏰ Time: `{timestamp_str}`\n"
            message += f"💰 Price: ₹{price:.2f}\n"
            message += f"📈 Volume: {vol_ratio:.2f}x average\n"
            return message
        else:
            emoji = "📊"
            signal_text = signal_type
            message = f"{emoji} *{signal_text}* - {symbol}\n\n"
            message += f"⏰ Time: `{timestamp_str}`\n"
            message += f"💰 Price: ₹{price:.2f}\n"
            return message
        
        # Format message
        message = f"{emoji} *{signal_text}* - {symbol}\n\n"
        message += f"⏰ Time: `{timestamp_str}`\n"
        message += f"💰 Price: ₹{price:.2f}\n"
        message += f"📊 Level: ₹{level:.2f} ({direction})\n"
        message += f"📈 Volume: {vol_ratio:.2f}x average\n"
        
        return message
    
    def _format_pattern_alert(self, alert: Dict, pattern_type: str, symbol: str, price: float, timestamp_str: str) -> str:
        """
        Format pattern-based alert message.
        
        Args:
            alert: Alert dictionary
            pattern_type: Type of pattern detected
            symbol: Trading symbol
            price: Current price
            timestamp_str: Formatted timestamp string
            
        Returns:
            Formatted message string
        """
        if pattern_type == 'RSI_BULLISH_DIVERGENCE':
            emoji = "📈"
            pattern_name = "RSI Bullish Divergence"
            rsi = alert.get('rsi', 0)
            rsi_change = alert.get('rsi_change', 0)
            price_change_pct = alert.get('price_change_pct', 0)
            
            message = f"{emoji} *{pattern_name}* - {symbol}\n\n"
            message += f"⏰ Time: `{timestamp_str}`\n"
            message += f"💰 Price: ₹{price:.2f}\n"
            message += f"📊 RSI: {rsi:.2f}\n"
            message += f"📉 Price Change: {price_change_pct:.2f}%\n"
            message += f"📈 RSI Change: +{rsi_change:.2f}\n"
            message += f"\n💡 *Signal:* Potential reversal upward\n"
            message += f"🎯 *Entry:* Consider long position\n"
            message += f"🛑 *Stop Loss:* Below recent low\n"
            
        elif pattern_type == 'RSI_BEARISH_DIVERGENCE':
            emoji = "📉"
            pattern_name = "RSI Bearish Divergence"
            rsi = alert.get('rsi', 0)
            rsi_change = alert.get('rsi_change', 0)
            price_change_pct = alert.get('price_change_pct', 0)
            
            message = f"{emoji} *{pattern_name}* - {symbol}\n\n"
            message += f"⏰ Time: `{timestamp_str}`\n"
            message += f"💰 Price: ₹{price:.2f}\n"
            message += f"📊 RSI: {rsi:.2f}\n"
            message += f"📈 Price Change: +{price_change_pct:.2f}%\n"
            message += f"📉 RSI Change: {rsi_change:.2f}\n"
            message += f"\n💡 *Signal:* Potential reversal downward\n"
            message += f"🎯 *Entry:* Consider short position\n"
            message += f"🛑 *Stop Loss:* Above recent high\n"
            
        elif pattern_type == 'UPTREND_RETEST':
            emoji = "🟢"
            pattern_name = "Uptrend Retest (Break & Retest)"
            retest_level = alert.get('retest_level', 0)
            entry_price = alert.get('entry_price', price)
            stop_loss = alert.get('stop_loss', 0)
            target_price = alert.get('target_price', 0)
            vol_ratio = alert.get('vol_ratio', 0)
            bars_after = alert.get('bars_after_breakout', 0)
            
            message = f"{emoji} *{pattern_name}* - {symbol}\n\n"
            message += f"⏰ Time: `{timestamp_str}`\n"
            message += f"💰 Current Price: ₹{price:.2f}\n"
            message += f"📊 Retest Level: ₹{retest_level:.2f}\n"
            message += f"📈 Volume: {vol_ratio:.2f}x average\n"
            message += f"⏱️ Bars after breakout: {bars_after}\n"
            message += f"\n💡 *Signal:* Bullish retest confirmed\n"
            message += f"🎯 *Entry:* ₹{entry_price:.2f}\n"
            message += f"🛑 *Stop Loss:* ₹{stop_loss:.2f}\n"
            if target_price > 0:
                message += f"🎯 *Target:* ₹{target_price:.2f}\n"
            
        elif pattern_type == 'INVERSE_HEAD_SHOULDERS':
            emoji = "📈"
            pattern_name = "Inverse Head & Shoulders"
            neckline = alert.get('neckline', 0)
            head_price = alert.get('head_price', 0)
            entry_price = alert.get('entry_price', price)
            stop_loss = alert.get('stop_loss', 0)
            target_price = alert.get('target_price', 0)
            vol_ratio = alert.get('vol_ratio', 0)
            
            message = f"{emoji} *{pattern_name}* - {symbol}\n\n"
            message += f"⏰ Time: `{timestamp_str}`\n"
            message += f"💰 Current Price: ₹{price:.2f}\n"
            message += f"📊 Neckline: ₹{neckline:.2f}\n"
            message += f"📉 Head: ₹{head_price:.2f}\n"
            message += f"📈 Volume: {vol_ratio:.2f}x average\n"
            message += f"\n💡 *Signal:* Bullish reversal confirmed\n"
            message += f"🎯 *Entry:* ₹{entry_price:.2f}\n"
            message += f"🛑 *Stop Loss:* ₹{stop_loss:.2f}\n"
            if target_price > 0:
                message += f"🎯 *Target:* ₹{target_price:.2f}\n"
        
        elif pattern_type == 'DOUBLE_BOTTOM':
            emoji = "📈"
            pattern_name = "Double Bottom"
            neckline = alert.get('neckline', 0)
            entry_price = alert.get('entry_price', price)
            stop_loss = alert.get('stop_loss', 0)
            target_price = alert.get('target_price', 0)
            vol_ratio = alert.get('vol_ratio', 0)
            
            message = f"{emoji} *{pattern_name}* - {symbol}\n\n"
            message += f"⏰ Time: `{timestamp_str}`\n"
            message += f"💰 Current Price: ₹{price:.2f}\n"
            message += f"📊 Neckline: ₹{neckline:.2f}\n"
            message += f"📈 Volume: {vol_ratio:.2f}x average\n"
            message += f"\n💡 *Signal:* Bullish reversal confirmed\n"
            message += f"🎯 *Entry:* ₹{entry_price:.2f}\n"
            message += f"🛑 *Stop Loss:* ₹{stop_loss:.2f}\n"
            if target_price > 0:
                message += f"🎯 *Target:* ₹{target_price:.2f}\n"
        
        elif pattern_type == 'DOUBLE_TOP':
            emoji = "📉"
            pattern_name = "Double Top"
            neckline = alert.get('neckline', 0)
            entry_price = alert.get('entry_price', price)
            stop_loss = alert.get('stop_loss', 0)
            target_price = alert.get('target_price', 0)
            vol_ratio = alert.get('vol_ratio', 0)
            
            message = f"{emoji} *{pattern_name}* - {symbol}\n\n"
            message += f"⏰ Time: `{timestamp_str}`\n"
            message += f"💰 Current Price: ₹{price:.2f}\n"
            message += f"📊 Neckline: ₹{neckline:.2f}\n"
            message += f"📈 Volume: {vol_ratio:.2f}x average\n"
            message += f"\n💡 *Signal:* Bearish reversal confirmed\n"
            message += f"🎯 *Entry:* ₹{entry_price:.2f}\n"
            message += f"🛑 *Stop Loss:* ₹{stop_loss:.2f}\n"
            if target_price > 0:
                message += f"🎯 *Target:* ₹{target_price:.2f}\n"
        
        elif pattern_type == 'TRIPLE_BOTTOM':
            emoji = "📈"
            pattern_name = "Triple Bottom"
            neckline = alert.get('neckline', 0)
            entry_price = alert.get('entry_price', price)
            stop_loss = alert.get('stop_loss', 0)
            target_price = alert.get('target_price', 0)
            vol_ratio = alert.get('vol_ratio', 0)
            
            message = f"{emoji} *{pattern_name}* - {symbol}\n\n"
            message += f"⏰ Time: `{timestamp_str}`\n"
            message += f"💰 Current Price: ₹{price:.2f}\n"
            message += f"📊 Neckline: ₹{neckline:.2f}\n"
            message += f"📈 Volume: {vol_ratio:.2f}x average\n"
            message += f"\n💡 *Signal:* Strong bullish reversal confirmed\n"
            message += f"🎯 *Entry:* ₹{entry_price:.2f}\n"
            message += f"🛑 *Stop Loss:* ₹{stop_loss:.2f}\n"
            if target_price > 0:
                message += f"🎯 *Target:* ₹{target_price:.2f}\n"
        
        elif pattern_type == 'TRIPLE_TOP':
            emoji = "📉"
            pattern_name = "Triple Top"
            neckline = alert.get('neckline', 0)
            entry_price = alert.get('entry_price', price)
            stop_loss = alert.get('stop_loss', 0)
            target_price = alert.get('target_price', 0)
            vol_ratio = alert.get('vol_ratio', 0)
            
            message = f"{emoji} *{pattern_name}* - {symbol}\n\n"
            message += f"⏰ Time: `{timestamp_str}`\n"
            message += f"💰 Current Price: ₹{price:.2f}\n"
            message += f"📊 Neckline: ₹{neckline:.2f}\n"
            message += f"📈 Volume: {vol_ratio:.2f}x average\n"
            message += f"\n💡 *Signal:* Strong bearish reversal confirmed\n"
            message += f"🎯 *Entry:* ₹{entry_price:.2f}\n"
            message += f"🛑 *Stop Loss:* ₹{stop_loss:.2f}\n"
            if target_price > 0:
                message += f"🎯 *Target:* ₹{target_price:.2f}\n"
        
        elif pattern_type == 'DOWNTREND_RETEST':
            emoji = "🔴"
            pattern_name = "Downtrend Retest (Break & Retest)"
            retest_level = alert.get('retest_level', 0)
            entry_price = alert.get('entry_price', price)
            stop_loss = alert.get('stop_loss', 0)
            target_price = alert.get('target_price', 0)
            vol_ratio = alert.get('vol_ratio', 0)
            bars_after = alert.get('bars_after_breakdown', 0)
            
            message = f"{emoji} *{pattern_name}* - {symbol}\n\n"
            message += f"⏰ Time: `{timestamp_str}`\n"
            message += f"💰 Current Price: ₹{price:.2f}\n"
            message += f"📊 Retest Level: ₹{retest_level:.2f}\n"
            message += f"📈 Volume: {vol_ratio:.2f}x average\n"
            message += f"⏱️ Bars after breakdown: {bars_after}\n"
            message += f"\n💡 *Signal:* Bearish retest confirmed\n"
            message += f"🎯 *Entry:* ₹{entry_price:.2f}\n"
            message += f"🛑 *Stop Loss:* ₹{stop_loss:.2f}\n"
            if target_price > 0:
                message += f"🎯 *Target:* ₹{target_price:.2f}\n"
            
        else:
            # Fallback for unknown patterns
            message = f"📊 *{pattern_type}* - {symbol}\n\n"
            message += f"⏰ Time: `{timestamp_str}`\n"
            message += f"💰 Price: ₹{price:.2f}\n"
        
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

