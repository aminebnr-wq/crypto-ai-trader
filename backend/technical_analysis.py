"""
Technical Analysis Module
Calculates various technical indicators and generates signals
"""
import pandas as pd
import numpy as np
from ta import add_all_ta_features
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator, VolumeWeightedAveragePrice
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class TechnicalAnalyzer:
    """Advanced technical analysis for crypto trading"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize with OHLCV data
        
        Args:
            df: DataFrame with columns: open, high, low, close, volume
        """
        self.df = df.copy()
        self.signals = {}
        
    def calculate_all_indicators(self) -> pd.DataFrame:
        """Calculate all technical indicators"""
        try:
            # Add all TA features
            self.df = add_all_ta_features(
                self.df,
                open="open",
                high="high",
                low="low",
                close="close",
                volume="volume",
                fillna=True
            )
            
            # Additional custom indicators
            self._add_custom_indicators()
            
            logger.info(f"✅ Calculated {len(self.df.columns)} technical indicators")
            return self.df
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return self.df
    
    def _add_custom_indicators(self):
        """Add custom technical indicators"""
        # Moving Averages
        self.df['sma_20'] = SMAIndicator(self.df['close'], window=20).sma_indicator()
        self.df['sma_50'] = SMAIndicator(self.df['close'], window=50).sma_indicator()
        self.df['ema_12'] = EMAIndicator(self.df['close'], window=12).ema_indicator()
        self.df['ema_26'] = EMAIndicator(self.df['close'], window=26).ema_indicator()
        
        # Price action
        self.df['price_change'] = self.df['close'].pct_change() * 100
        self.df['volume_change'] = self.df['volume'].pct_change() * 100
        
    def analyze_trend(self) -> Dict:
        """Analyze market trend"""
        latest = self.df.iloc[-1]
        
        # Moving Average signals
        sma_signal = 1 if latest['close'] > latest['sma_20'] else -1
        ema_signal = 1 if latest['ema_12'] > latest['ema_26'] else -1
        
        # MACD signal
        macd_signal = 1 if latest.get('trend_macd', 0) > latest.get('trend_macd_signal', 0) else -1
        
        # Overall trend
        trend_score = sma_signal + ema_signal + macd_signal
        
        return {
            'trend': 'bullish' if trend_score > 0 else 'bearish' if trend_score < 0 else 'neutral',
            'trend_strength': abs(trend_score) / 3 * 100,
            'sma_signal': sma_signal,
            'ema_signal': ema_signal,
            'macd_signal': macd_signal,
        }
    
    def analyze_momentum(self) -> Dict:
        """Analyze momentum indicators"""
        latest = self.df.iloc[-1]
        
        # RSI analysis
        rsi = latest.get('momentum_rsi', 50)
        rsi_signal = 'oversold' if rsi < 30 else 'overbought' if rsi > 70 else 'neutral'
        
        # Stochastic analysis
        stoch = latest.get('momentum_stoch', 50)
        stoch_signal = 'oversold' if stoch < 20 else 'overbought' if stoch > 80 else 'neutral'
        
        return {
            'rsi': rsi,
            'rsi_signal': rsi_signal,
            'stochastic': stoch,
            'stoch_signal': stoch_signal,
            'momentum_score': self._calculate_momentum_score(rsi, stoch)
        }
    
    def analyze_volatility(self) -> Dict:
        """Analyze volatility and support/resistance"""
        latest = self.df.iloc[-1]
        
        # Bollinger Bands
        bb_high = latest.get('volatility_bbh', 0)
        bb_low = latest.get('volatility_bbl', 0)
        bb_mid = latest.get('volatility_bbm', 0)
        price = latest['close']
        
        # Position within bands
        if bb_high != bb_low:
            bb_position = (price - bb_low) / (bb_high - bb_low) * 100
        else:
            bb_position = 50
        
        # ATR for volatility
        atr = latest.get('volatility_atr', 0)
        
        return {
            'bb_upper': bb_high,
            'bb_middle': bb_mid,
            'bb_lower': bb_low,
            'bb_position': bb_position,
            'atr': atr,
            'volatility_signal': 'high' if atr > self.df['volatility_atr'].mean() else 'low'
        }
    
    def analyze_volume(self) -> Dict:
        """Analyze volume indicators"""
        latest = self.df.iloc[-1]
        avg_volume = self.df['volume'].tail(20).mean()
        
        volume_ratio = latest['volume'] / avg_volume if avg_volume > 0 else 1
        
        return {
            'current_volume': latest['volume'],
            'avg_volume': avg_volume,
            'volume_ratio': volume_ratio,
            'volume_signal': 'high' if volume_ratio > 1.5 else 'low' if volume_ratio < 0.5 else 'normal',
            'obv': latest.get('volume_obv', 0)
        }
    
    def _calculate_momentum_score(self, rsi: float, stoch: float) -> float:
        """Calculate overall momentum score (0-100)"""
        # Normalize RSI and Stochastic
        rsi_score = rsi
        stoch_score = stoch
        
        # Average
        return (rsi_score + stoch_score) / 2
    
    def generate_trading_signal(self) -> Dict:
        """
        Generate comprehensive trading signal
        
        Returns:
            Dict with signal, confidence, and analysis
        """
        trend = self.analyze_trend()
        momentum = self.analyze_momentum()
        volatility = self.analyze_volatility()
        volume = self.analyze_volume()
        
        # Calculate confidence score
        confidence = self._calculate_confidence(trend, momentum, volatility, volume)
        
        # Determine signal
        signal = self._determine_signal(trend, momentum, volatility, volume, confidence)
        
        return {
            'signal': signal,
            'confidence': confidence,
            'trend_analysis': trend,
            'momentum_analysis': momentum,
            'volatility_analysis': volatility,
            'volume_analysis': volume,
            'current_price': self.df.iloc[-1]['close'],
            'timestamp': self.df.iloc[-1]['timestamp']
        }
    
    def _calculate_confidence(
        self,
        trend: Dict,
        momentum: Dict,
        volatility: Dict,
        volume: Dict
    ) -> float:
        """Calculate overall confidence score (0-100)"""
        scores = []
        
        # Trend confidence (30%)
        if trend['trend'] != 'neutral':
            scores.append(trend['trend_strength'] * 0.3)
        
        # Momentum confidence (25%)
        if momentum['rsi_signal'] in ['oversold', 'overbought']:
            scores.append(75 * 0.25)  # Strong signal
        else:
            scores.append(50 * 0.25)
        
        # Volume confirmation (25%)
        if volume['volume_signal'] == 'high':
            scores.append(80 * 0.25)
        elif volume['volume_signal'] == 'normal':
            scores.append(60 * 0.25)
        else:
            scores.append(40 * 0.25)
        
        # Volatility consideration (20%)
        if volatility['volatility_signal'] == 'low':
            scores.append(70 * 0.2)  # Prefer lower volatility
        else:
            scores.append(50 * 0.2)
        
        return sum(scores)
    
    def _determine_signal(
        self,
        trend: Dict,
        momentum: Dict,
        volatility: Dict,
        volume: Dict,
        confidence: float
    ) -> str:
        """Determine buy/sell/hold signal"""
        buy_signals = 0
        sell_signals = 0
        
        # Trend signals
        if trend['trend'] == 'bullish':
            buy_signals += trend['trend_strength'] / 100 * 2
        elif trend['trend'] == 'bearish':
            sell_signals += trend['trend_strength'] / 100 * 2
        
        # Momentum signals
        if momentum['rsi_signal'] == 'oversold':
            buy_signals += 2
        elif momentum['rsi_signal'] == 'overbought':
            sell_signals += 2
        
        # Volume confirmation
        if volume['volume_signal'] == 'high':
            if buy_signals > sell_signals:
                buy_signals += 1
            elif sell_signals > buy_signals:
                sell_signals += 1
        
        # Price position in Bollinger Bands
        if volatility['bb_position'] < 20:
            buy_signals += 1
        elif volatility['bb_position'] > 80:
            sell_signals += 1
        
        # Determine final signal
        if buy_signals > sell_signals and confidence >= 60:
            return 'BUY'
        elif sell_signals > buy_signals and confidence >= 60:
            return 'SELL'
        else:
            return 'HOLD'
    
    def get_support_resistance(self, window: int = 20) -> Tuple[float, float]:
        """Calculate support and resistance levels"""
        recent_data = self.df.tail(window)
        
        resistance = recent_data['high'].max()
        support = recent_data['low'].min()
        
        return support, resistance


if __name__ == "__main__":
    # Test with sample data
    from binance_client import BinanceDataFetcher
    
    fetcher = BinanceDataFetcher()
    df = fetcher.get_historical_data('BTC', interval='1h', days=30)
    
    analyzer = TechnicalAnalyzer(df)
    analyzer.calculate_all_indicators()
    
    signal = analyzer.generate_trading_signal()
    print(f"\n📊 Trading Signal Analysis:")
    print(f"Signal: {signal['signal']}")
    print(f"Confidence: {signal['confidence']:.2f}%")
    print(f"Trend: {signal['trend_analysis']}")
    print(f"Momentum: {signal['momentum_analysis']}")
