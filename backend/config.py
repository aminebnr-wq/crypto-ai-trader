"""
Configuration management for the AI Trading System
"""
from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    BINANCE_API_KEY: str = ""
    BINANCE_SECRET_KEY: str = ""
    
    # Database
    DATABASE_URL: str = "sqlite:///./crypto_trader.db"
    
    # Email Notifications
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_USER: str = ""
    EMAIL_PASSWORD: str = ""
    NOTIFICATION_EMAIL: str = ""
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    
    # News API
    NEWS_API_KEY: str = ""
    
    # Twitter API
    TWITTER_BEARER_TOKEN: str = ""
    
    # Trading Parameters
    MIN_CONFIDENCE_SCORE: float = 80.0
    TARGET_PROFIT_PERCENT: float = 3.0
    STOP_LOSS_PERCENT: float = 1.0
    MAX_TRADE_AMOUNT_USDT: float = 100.0
    
    # Monitoring
    WATCH_COINS: str = "BTC,ETH,BNB,SOL,ADA"
    
    # System
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    DATA_DIR: str = "data"
    
    @property
    def coins_list(self) -> List[str]:
        """Get list of coins to monitor"""
        return [coin.strip() for coin in self.WATCH_COINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
