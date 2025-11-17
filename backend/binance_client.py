"""
Binance API Client for fetching market data
"""
from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from config import settings

logger = logging.getLogger(__name__)


class BinanceDataFetcher:
    """Fetch and process data from Binance"""
    
    def __init__(self):
        try:
            self.client = Client(
                settings.BINANCE_API_KEY,
                settings.BINANCE_SECRET_KEY,
                testnet=False
            )
            logger.info("✅ Binance client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Binance client: {e}")
            raise
    
    def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        try:
            ticker = self.client.get_symbol_ticker(symbol=f"{symbol}USDT")
            return float(ticker['price'])
        except BinanceAPIException as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return 0.0
    
    def get_historical_data(
        self,
        symbol: str,
        interval: str = '1h',
        days: int = 30
    ) -> pd.DataFrame:
        """
        Get historical OHLCV data
        
        Args:
            symbol: Trading pair (e.g., 'BTC')
            interval: Candle interval (1m, 5m, 15m, 1h, 4h, 1d)
            days: Number of days of historical data
        """
        try:
            # Calculate start time
            start_time = datetime.now() - timedelta(days=days)
            start_str = start_time.strftime("%d %b %Y %H:%M:%S")
            
            # Fetch klines
            klines = self.client.get_historical_klines(
                f"{symbol}USDT",
                interval,
                start_str
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Process data
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            
            # Convert to numeric
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            logger.info(f"✅ Fetched {len(df)} candles for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_24h_stats(self, symbol: str) -> Dict:
        """Get 24-hour statistics for a symbol"""
        try:
            ticker = self.client.get_ticker(symbol=f"{symbol}USDT")
            return {
                'price': float(ticker['lastPrice']),
                'change_percent': float(ticker['priceChangePercent']),
                'high_24h': float(ticker['highPrice']),
                'low_24h': float(ticker['lowPrice']),
                'volume_24h': float(ticker['volume']),
                'quote_volume_24h': float(ticker['quoteVolume']),
            }
        except Exception as e:
            logger.error(f"Error fetching 24h stats for {symbol}: {e}")
            return {}
    
    def get_order_book(self, symbol: str, limit: int = 10) -> Dict:
        """Get order book depth"""
        try:
            depth = self.client.get_order_book(symbol=f"{symbol}USDT", limit=limit)
            return {
                'bids': depth['bids'],
                'asks': depth['asks'],
                'bid_volume': sum(float(bid[1]) for bid in depth['bids']),
                'ask_volume': sum(float(ask[1]) for ask in depth['asks']),
            }
        except Exception as e:
            logger.error(f"Error fetching order book for {symbol}: {e}")
            return {}
    
    def check_api_permissions(self) -> Dict[str, bool]:
        """Check API key permissions"""
        try:
            account = self.client.get_account()
            return {
                'can_trade': account['canTrade'],
                'can_withdraw': account['canWithdraw'],
                'can_deposit': account['canDeposit'],
            }
        except Exception as e:
            logger.error(f"Error checking permissions: {e}")
            return {}


if __name__ == "__main__":
    # Test the client
    fetcher = BinanceDataFetcher()
    
    # Check permissions
    perms = fetcher.check_api_permissions()
    print(f"\n🔐 API Permissions: {perms}")
    
    # Get BTC price
    btc_price = fetcher.get_current_price('BTC')
    print(f"\n💰 BTC Price: ${btc_price:,.2f}")
    
    # Get 24h stats
    stats = fetcher.get_24h_stats('BTC')
    print(f"\n📊 24h Stats: {stats}")
    
    # Get historical data
    df = fetcher.get_historical_data('BTC', interval='1h', days=7)
    print(f"\n📈 Historical Data Shape: {df.shape}")
    print(df.tail())
