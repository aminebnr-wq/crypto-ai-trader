"""
FastAPI Backend - Main API Server
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging
from datetime import datetime
import json
import os

from signal_generator import AISignalGenerator
from binance_client import BinanceDataFetcher
from notifications import NotificationService
from config import settings

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Crypto Trading Signal System",
    description="Advanced AI-powered cryptocurrency trading signals",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
signal_generator = AISignalGenerator()
notification_service = NotificationService()
binance_client = BinanceDataFetcher()

# Data models
class SignalResponse(BaseModel):
    coin: str
    timestamp: str
    action: str
    confidence: float
    current_price: float
    entry_price: Optional[float] = None
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    potential_profit_percent: Optional[float] = None
    risk_level: str
    scores: Dict
    analysis: Dict
    reasoning: List[str]


class CoinScanRequest(BaseModel):
    coin: str
    retrain_lstm: bool = False


# Routes
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "AI Crypto Trading Signal System API",
        "version": "1.0.0",
        "endpoints": {
            "/signals/scan/{coin}": "Get trading signal for a specific coin",
            "/signals/scan-all": "Scan all configured coins",
            "/signals/latest": "Get latest generated signals",
            "/market/price/{coin}": "Get current price",
            "/market/stats/{coin}": "Get 24h statistics",
            "/health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Binance connection
        btc_price = binance_client.get_current_price('BTC')
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "binance_connected": btc_price > 0,
            "services": {
                "signal_generator": True,
                "binance_client": True,
                "notifications": {
                    "email": notification_service.email_enabled,
                    "telegram": notification_service.telegram_enabled
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.get("/signals/scan/{coin}")
async def scan_coin(
    coin: str,
    retrain_lstm: bool = False,
    background_tasks: BackgroundTasks = None
):
    """
    Generate trading signal for a specific cryptocurrency
    
    Args:
        coin: Cryptocurrency symbol (BTC, ETH, etc.)
        retrain_lstm: Whether to retrain the LSTM model
    """
    try:
        logger.info(f"📊 Scanning {coin}...")
        
        # Generate signal
        signal = signal_generator.analyze_coin(coin, retrain_lstm=retrain_lstm)
        
        if 'error' in signal:
            raise HTTPException(status_code=500, detail=signal['error'])
        
        # Save signal
        _save_signal(signal)
        
        # Send notification in background if not HOLD
        if signal['action'] != 'HOLD' and background_tasks:
            background_tasks.add_task(
                notification_service.send_signal_notification,
                signal
            )
        
        return signal
        
    except Exception as e:
        logger.error(f"Error scanning {coin}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/signals/scan-all")
async def scan_all_coins(background_tasks: BackgroundTasks = None):
    """Scan all configured coins and return high-confidence signals"""
    try:
        logger.info("🔍 Scanning all configured coins...")
        
        signals = signal_generator.scan_all_coins()
        
        # Save all signals
        for signal in signals:
            _save_signal(signal)
        
        # Send notifications for high-confidence signals
        if background_tasks:
            for signal in signals:
                if signal['confidence'] >= settings.MIN_CONFIDENCE_SCORE:
                    background_tasks.add_task(
                        notification_service.send_signal_notification,
                        signal
                    )
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_signals": len(signals),
            "signals": signals
        }
        
    except Exception as e:
        logger.error(f"Error scanning all coins: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/signals/latest")
async def get_latest_signals(limit: int = 10):
    """Get latest generated signals"""
    try:
        signals_file = os.path.join(settings.DATA_DIR, "signals_history.json")
        
        if not os.path.exists(signals_file):
            return {"signals": []}
        
        with open(signals_file, 'r') as f:
            all_signals = json.load(f)
        
        # Return latest signals
        return {
            "signals": all_signals[-limit:][::-1]  # Reverse to show newest first
        }
        
    except Exception as e:
        logger.error(f"Error getting latest signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/market/price/{coin}")
async def get_price(coin: str):
    """Get current price for a cryptocurrency"""
    try:
        price = binance_client.get_current_price(coin)
        
        if price == 0:
            raise HTTPException(status_code=404, detail=f"Price not found for {coin}")
        
        return {
            "coin": coin,
            "price": price,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting price for {coin}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/market/stats/{coin}")
async def get_stats(coin: str):
    """Get 24-hour statistics for a cryptocurrency"""
    try:
        stats = binance_client.get_24h_stats(coin)
        
        if not stats:
            raise HTTPException(status_code=404, detail=f"Stats not found for {coin}")
        
        return {
            "coin": coin,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting stats for {coin}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/config/coins")
async def get_configured_coins():
    """Get list of configured coins to monitor"""
    return {
        "coins": settings.coins_list,
        "min_confidence": settings.MIN_CONFIDENCE_SCORE,
        "target_profit": settings.TARGET_PROFIT_PERCENT,
        "stop_loss": settings.STOP_LOSS_PERCENT
    }


def _save_signal(signal: Dict):
    """Save signal to history file"""
    try:
        os.makedirs(settings.DATA_DIR, exist_ok=True)
        signals_file = os.path.join(settings.DATA_DIR, "signals_history.json")
        
        # Load existing signals
        if os.path.exists(signals_file):
            with open(signals_file, 'r') as f:
                signals = json.load(f)
        else:
            signals = []
        
        # Append new signal
        signals.append(signal)
        
        # Keep only last 100 signals
        signals = signals[-100:]
        
        # Save
        with open(signals_file, 'w') as f:
            json.dump(signals, f, indent=2)
        
        logger.info(f"✅ Signal saved to history")
        
    except Exception as e:
        logger.error(f"Error saving signal: {e}")


if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting AI Trading Signal API Server...")
    logger.info(f"📊 Monitoring coins: {settings.coins_list}")
    logger.info(f"⚙️ Min confidence: {settings.MIN_CONFIDENCE_SCORE}%")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=settings.LOG_LEVEL.lower()
    )
