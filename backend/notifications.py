"""
Notification System - Email and Telegram
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict
import logging
from config import settings
import asyncio
import aiosmtplib

logger = logging.getLogger(__name__)


class NotificationService:
    """Send trading signals via email and Telegram"""
    
    def __init__(self):
        self.email_enabled = bool(settings.EMAIL_USER and settings.EMAIL_PASSWORD)
        self.telegram_enabled = bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID)
        
        if self.telegram_enabled:
            try:
                from telegram import Bot
                self.telegram_bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
            except ImportError:
                logger.warning("python-telegram-bot not installed. Telegram notifications disabled.")
                self.telegram_enabled = False
    
    async def send_signal_notification(self, signal: Dict):
        """Send notification for a trading signal"""
        if signal['action'] == 'HOLD':
            logger.info("Signal is HOLD - no notification sent")
            return
        
        # Send via email
        if self.email_enabled:
            await self._send_email(signal)
        
        # Send via Telegram
        if self.telegram_enabled:
            await self._send_telegram(signal)
    
    async def _send_email(self, signal: Dict):
        """Send email notification"""
        try:
            subject = f"🚨 {signal['action']} Signal for {signal['coin']} - {signal['confidence']}% Confidence"
            
            # Create HTML email
            html = self._create_email_html(signal)
            
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = settings.EMAIL_USER
            message['To'] = settings.NOTIFICATION_EMAIL
            
            html_part = MIMEText(html, 'html')
            message.attach(html_part)
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_USER,
                password=settings.EMAIL_PASSWORD,
                start_tls=True
            )
            
            logger.info(f"✅ Email notification sent for {signal['coin']}")
            
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
    
    def _create_email_html(self, signal: Dict) -> str:
        """Create HTML email content"""
        action_color = '#10b981' if signal['action'] == 'BUY' else '#ef4444'
        action_emoji = '📈' if signal['action'] == 'BUY' else '📉'
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f3f4f6; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; padding: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .action {{ font-size: 32px; font-weight: bold; color: {action_color}; margin: 10px 0; }}
                .coin {{ font-size: 28px; color: #1f2937; }}
                .confidence {{ font-size: 24px; color: #6b7280; }}
                .price-box {{ background-color: #f9fafb; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .price-item {{ display: flex; justify-content: space-between; margin: 10px 0; }}
                .label {{ color: #6b7280; }}
                .value {{ font-weight: bold; color: #1f2937; }}
                .reasoning {{ background-color: #eff6ff; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                .reason-item {{ margin: 8px 0; color: #1e40af; }}
                .footer {{ text-align: center; margin-top: 30px; color: #9ca3af; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="action">{action_emoji} {signal['action']}</div>
                    <div class="coin">{signal['coin']}/USDT</div>
                    <div class="confidence">Confidence: {signal['confidence']}%</div>
                </div>
                
                <div class="price-box">
                    <div class="price-item">
                        <span class="label">Current Price:</span>
                        <span class="value">${signal['current_price']:,.2f}</span>
                    </div>
                    <div class="price-item">
                        <span class="label">Entry Price:</span>
                        <span class="value">${signal['entry_price']:,.2f}</span>
                    </div>
                    <div class="price-item">
                        <span class="label">Target Price:</span>
                        <span class="value" style="color: #10b981;">${signal['target_price']:,.2f}</span>
                    </div>
                    <div class="price-item">
                        <span class="label">Stop Loss:</span>
                        <span class="value" style="color: #ef4444;">${signal['stop_loss']:,.2f}</span>
                    </div>
                    <div class="price-item">
                        <span class="label">Potential Profit:</span>
                        <span class="value" style="color: #10b981;">{signal['potential_profit_percent']}%</span>
                    </div>
                    <div class="price-item">
                        <span class="label">Risk Level:</span>
                        <span class="value">{signal['risk_level']}</span>
                    </div>
                </div>
                
                <div class="reasoning">
                    <strong>📊 Analysis Reasoning:</strong>
                    {''.join(f'<div class="reason-item">• {reason}</div>' for reason in signal['reasoning'])}
                </div>
                
                <div class="footer">
                    Generated by AI Trading System | {signal['timestamp']}
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    async def _send_telegram(self, signal: Dict):
        """Send Telegram notification"""
        try:
            action_emoji = '📈' if signal['action'] == 'BUY' else '📉'
            
            message = f"""
🚨 *{action_emoji} {signal['action']} SIGNAL* 🚨

*Coin:* {signal['coin']}/USDT
*Confidence:* {signal['confidence']}%

💰 *Prices:*
Current: ${signal['current_price']:,.2f}
Entry: ${signal['entry_price']:,.2f}
Target: ${signal['target_price']:,.2f} ({'+'}{signal['potential_profit_percent']}%)
Stop Loss: ${signal['stop_loss']:,.2f}

⚠️ *Risk Level:* {signal['risk_level']}

📊 *Analysis Scores:*
Technical: {signal['scores']['technical']}%
AI Prediction: {signal['scores']['ai_prediction']}%
Sentiment: {signal['scores']['sentiment']}%

📝 *Reasoning:*
{chr(10).join('• ' + reason for reason in signal['reasoning'])}

🕐 {signal['timestamp']}
            """
            
            await self.telegram_bot.send_message(
                chat_id=settings.TELEGRAM_CHAT_ID,
                text=message,
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ Telegram notification sent for {signal['coin']}")
            
        except Exception as e:
            logger.error(f"❌ Failed to send Telegram message: {e}")
    
    def send_test_notification(self):
        """Send test notification to verify setup"""
        test_signal = {
            'coin': 'BTC',
            'action': 'BUY',
            'confidence': 85.5,
            'current_price': 43250.00,
            'entry_price': 43250.00,
            'target_price': 44500.00,
            'stop_loss': 42800.00,
            'potential_profit_percent': 2.9,
            'risk_level': 'MEDIUM',
            'scores': {
                'technical': 82,
                'ai_prediction': 88,
                'sentiment': 75
            },
            'reasoning': [
                '📈 Strong bullish trend detected',
                '💎 RSI indicates oversold condition',
                '🤖 AI predicts 3.2% increase in next 24h'
            ],
            'timestamp': '2025-11-17T08:00:00'
        }
        
        asyncio.run(self.send_signal_notification(test_signal))


if __name__ == "__main__":
    # Test notifications
    notifier = NotificationService()
    print("\n📧 Sending test notification...")
    notifier.send_test_notification()
    print("✅ Check your email and Telegram!")
