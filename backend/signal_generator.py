"""
Main AI Trading Signal Generator
Combines all analysis methods to generate high-confidence signals
"""
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import logging
from binance_client import BinanceDataFetcher
from technical_analysis import TechnicalAnalyzer
from news_sentiment import NewsAnalyzer
from lstm_predictor import LSTMPricePredictor
from config import settings
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AISignalGenerator:
    """
    Advanced AI-powered trading signal generator
    Combines technical analysis, sentiment analysis, and LSTM predictions
    """
    
    def __init__(self):
        self.binance = BinanceDataFetcher()
        self.news_analyzer = NewsAnalyzer()
        self.lstm_predictors = {}  # One predictor per coin
        
        logger.info("✅ AI Signal Generator initialized")
    
    def analyze_coin(self, coin: str, retrain_lstm: bool = False) -> Dict:
        """
        Comprehensive analysis of a cryptocurrency
        
        Args:
            coin: Cryptocurrency symbol (e.g., 'BTC')
            retrain_lstm: Whether to retrain LSTM model
            
        Returns:
            Complete analysis with signal recommendation
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"🔍 Analyzing {coin}...")
        logger.info(f"{'='*60}")
        
        # 1. Fetch market data
        logger.info("📊 Fetching market data...")
        df = self.binance.get_historical_data(coin, interval='1h', days=60)
        stats_24h = self.binance.get_24h_stats(coin)
        
        if df.empty:
            logger.error(f"❌ Failed to fetch data for {coin}")
            return {'error': 'Data fetch failed'}
        
        # 2. Technical Analysis
        logger.info("📈 Performing technical analysis...")
        tech_analyzer = TechnicalAnalyzer(df)
        tech_analyzer.calculate_all_indicators()
        tech_signal = tech_analyzer.generate_trading_signal()
        
        # 3. Sentiment Analysis
        logger.info("📰 Analyzing news sentiment...")
        sentiment = self.news_analyzer.get_coin_sentiment(coin)
        major_events = self.news_analyzer.check_major_events(coin)
        
        # 4. LSTM Prediction
        logger.info("🤖 Running AI price prediction...")
        if coin not in self.lstm_predictors or retrain_lstm:
            self.lstm_predictors[coin] = LSTMPricePredictor(lookback=60, forecast_steps=24)
            
            # Train model if not trained
            if not self.lstm_predictors[coin].is_trained:
                logger.info("🎓 Training LSTM model (this may take a few minutes)...")
                self.lstm_predictors[coin].train(df, epochs=30, batch_size=32)
        
        lstm_prediction = self.lstm_predictors[coin].predict(df)
        
        # 5. Combine all signals
        final_signal = self._generate_final_signal(
            coin=coin,
            tech_signal=tech_signal,
            sentiment=sentiment,
            lstm_prediction=lstm_prediction,
            stats_24h=stats_24h,
            major_events=major_events
        )
        
        return final_signal
    
    def _generate_final_signal(
        self,
        coin: str,
        tech_signal: Dict,
        sentiment: Dict,
        lstm_prediction: Dict,
        stats_24h: Dict,
        major_events: List
    ) -> Dict:
        """
        Generate final trading signal by combining all analysis
        
        Returns:
            Complete signal with entry/exit points and confidence
        """
        current_price = tech_signal['current_price']
        
        # Calculate component scores (0-100 each)
        tech_score = self._calculate_tech_score(tech_signal)
        sentiment_score = self._calculate_sentiment_score(sentiment)
        lstm_score = self._calculate_lstm_score(lstm_prediction)
        
        # Weighted average (Technical 40%, LSTM 35%, Sentiment 25%)
        final_confidence = (
            tech_score * 0.40 +
            lstm_score * 0.35 +
            sentiment_score * 0.25
        )
        
        # Determine final action
        action = self._determine_action(
            tech_signal['signal'],
            lstm_prediction.get('direction', 'neutral'),
            sentiment['overall_sentiment'],
            final_confidence
        )
        
        # Calculate entry/exit points
        entry_price = current_price
        target_price, stop_loss = self._calculate_targets(
            current_price,
            action,
            tech_signal,
            lstm_prediction
        )
        
        # Risk assessment
        risk_level = self._assess_risk(
            final_confidence,
            stats_24h,
            major_events,
            tech_signal['volatility_analysis']
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            tech_signal,
            sentiment,
            lstm_prediction,
            major_events
        )
        
        signal = {
            'coin': coin,
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'confidence': round(final_confidence, 2),
            'current_price': round(current_price, 2),
            'entry_price': round(entry_price, 2),
            'target_price': round(target_price, 2) if target_price else None,
            'stop_loss': round(stop_loss, 2) if stop_loss else None,
            'potential_profit_percent': round(((target_price - entry_price) / entry_price * 100), 2) if target_price and action == 'BUY' else None,
            'risk_level': risk_level,
            'risk_reward_ratio': round(abs((target_price - entry_price) / (entry_price - stop_loss)), 2) if target_price and stop_loss and stop_loss != entry_price else None,
            'scores': {
                'technical': round(tech_score, 2),
                'ai_prediction': round(lstm_score, 2),
                'sentiment': round(sentiment_score, 2)
            },
            'analysis': {
                'technical': {
                    'trend': tech_signal['trend_analysis']['trend'],
                    'rsi': tech_signal['momentum_analysis']['rsi'],
                    'volume_signal': tech_signal['volume_analysis']['volume_signal']
                },
                'ai_prediction': {
                    'predicted_price': round(lstm_prediction.get('predicted_price', 0), 2),
                    'direction': lstm_prediction.get('direction', 'unknown'),
                    'change_percent': round(lstm_prediction.get('price_change_percent', 0), 2)
                },
                'sentiment': {
                    'overall': sentiment['overall_sentiment'],
                    'score': round(sentiment['sentiment_score'], 2),
                    'news_count': sentiment['news_count']
                },
                'market': {
                    'change_24h': round(stats_24h.get('change_percent', 0), 2),
                    'volume_24h': round(stats_24h.get('volume_24h', 0), 2),
                    'high_24h': round(stats_24h.get('high_24h', 0), 2),
                    'low_24h': round(stats_24h.get('low_24h', 0), 2)
                }
            },
            'reasoning': reasoning,
            'major_events': major_events[:3] if major_events else []
        }
        
        # Log signal
        self._log_signal(signal)
        
        return signal
    
    def _calculate_tech_score(self, tech_signal: Dict) -> float:
        """Calculate technical analysis score (0-100)"""
        score = tech_signal['confidence']
        
        # Bonus for strong signals
        if tech_signal['signal'] in ['BUY', 'SELL']:
            score += 10
        
        return min(100, score)
    
    def _calculate_sentiment_score(self, sentiment: Dict) -> float:
        """Calculate sentiment score (0-100)"""
        base_score = (sentiment['sentiment_score'] + 100) / 2  # Scale -100,100 to 0,100
        
        # Weight by confidence
        weighted_score = base_score * (sentiment['confidence'] / 100)
        
        # Bonus for high news volume
        if sentiment['news_count'] >= 5:
            weighted_score += 10
        
        return min(100, max(0, weighted_score))
    
    def _calculate_lstm_score(self, lstm_prediction: Dict) -> float:
        """Calculate LSTM prediction score (0-100)"""
        if 'error' in lstm_prediction:
            return 50  # Neutral if no prediction
        
        confidence = lstm_prediction.get('confidence', 50)
        
        # Adjust based on prediction magnitude
        change_percent = abs(lstm_prediction.get('price_change_percent', 0))
        if 1 <= change_percent <= 5:  # Ideal range
            confidence += 10
        elif change_percent > 10:  # Too extreme
            confidence -= 20
        
        return min(100, max(0, confidence))
    
    def _determine_action(
        self,
        tech_signal: str,
        lstm_direction: str,
        sentiment: str,
        confidence: float
    ) -> str:
        """Determine final trading action"""
        
        # Require minimum confidence
        if confidence < settings.MIN_CONFIDENCE_SCORE:
            return 'HOLD'
        
        # Count bullish signals
        bullish_signals = 0
        bearish_signals = 0
        
        if tech_signal == 'BUY':
            bullish_signals += 2
        elif tech_signal == 'SELL':
            bearish_signals += 2
        
        if lstm_direction == 'up':
            bullish_signals += 2
        elif lstm_direction == 'down':
            bearish_signals += 2
        
        if sentiment == 'positive':
            bullish_signals += 1
        elif sentiment == 'negative':
            bearish_signals += 1
        
        # Make decision
        if bullish_signals >= 4 and bullish_signals > bearish_signals:
            return 'BUY'
        elif bearish_signals >= 4 and bearish_signals > bullish_signals:
            return 'SELL'
        else:
            return 'HOLD'
    
    def _calculate_targets(
        self,
        current_price: float,
        action: str,
        tech_signal: Dict,
        lstm_prediction: Dict
    ) -> tuple:
        """Calculate target and stop-loss prices"""
        
        if action == 'HOLD':
            return None, None
        
        if action == 'BUY':
            # Target: Use LSTM prediction or default %
            if 'predicted_price' in lstm_prediction:
                target = lstm_prediction['predicted_price']
            else:
                target = current_price * (1 + settings.TARGET_PROFIT_PERCENT / 100)
            
            # Stop loss
            stop_loss = current_price * (1 - settings.STOP_LOSS_PERCENT / 100)
            
        else:  # SELL
            target = current_price * (1 - settings.TARGET_PROFIT_PERCENT / 100)
            stop_loss = current_price * (1 + settings.STOP_LOSS_PERCENT / 100)
        
        return target, stop_loss
    
    def _assess_risk(
        self,
        confidence: float,
        stats_24h: Dict,
        major_events: List,
        volatility: Dict
    ) -> str:
        """Assess overall risk level"""
        risk_score = 0
        
        # Low confidence = higher risk
        if confidence < 70:
            risk_score += 2
        elif confidence < 85:
            risk_score += 1
        
        # High volatility = higher risk
        if volatility['volatility_signal'] == 'high':
            risk_score += 2
        
        # Major events = higher risk
        if len(major_events) > 0:
            risk_score += 1
        
        # Large 24h change = higher risk
        if abs(stats_24h.get('change_percent', 0)) > 10:
            risk_score += 1
        
        if risk_score <= 1:
            return 'LOW'
        elif risk_score <= 3:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def _generate_reasoning(
        self,
        tech_signal: Dict,
        sentiment: Dict,
        lstm_prediction: Dict,
        major_events: List
    ) -> List[str]:
        """Generate human-readable reasoning"""
        reasons = []
        
        # Technical reasons
        trend = tech_signal['trend_analysis']
        if trend['trend'] == 'bullish':
            reasons.append(f"📈 Strong bullish trend detected ({trend['trend_strength']:.0f}% strength)")
        elif trend['trend'] == 'bearish':
            reasons.append(f"📉 Bearish trend detected ({trend['trend_strength']:.0f}% strength)")
        
        # RSI
        rsi = tech_signal['momentum_analysis']['rsi']
        if rsi < 30:
            reasons.append(f"💎 RSI indicates oversold condition ({rsi:.1f})")
        elif rsi > 70:
            reasons.append(f"⚠️ RSI indicates overbought condition ({rsi:.1f})")
        
        # Volume
        volume = tech_signal['volume_analysis']
        if volume['volume_signal'] == 'high':
            reasons.append(f"📊 High trading volume confirms movement ({volume['volume_ratio']:.1f}x average)")
        
        # AI prediction
        if 'predicted_price' in lstm_prediction:
            change = lstm_prediction['price_change_percent']
            if abs(change) > 2:
                direction = "increase" if change > 0 else "decrease"
                reasons.append(f"🤖 AI predicts {abs(change):.1f}% {direction} in next 24h")
        
        # Sentiment
        if sentiment['overall_sentiment'] != 'neutral':
            reasons.append(f"📰 News sentiment is {sentiment['overall_sentiment']} ({sentiment['news_count']} recent articles)")
        
        # Major events
        if major_events:
            reasons.append(f"⚠️ {len(major_events)} major event(s) detected - proceed with caution")
        
        return reasons
    
    def _log_signal(self, signal: Dict):
        """Log signal to console and file"""
        logger.info(f"\n{'='*60}")
        logger.info(f"🎯 SIGNAL GENERATED FOR {signal['coin']}")
        logger.info(f"{'='*60}")
        logger.info(f"Action: {signal['action']}")
        logger.info(f"Confidence: {signal['confidence']}%")
        logger.info(f"Current Price: ${signal['current_price']:,.2f}")
        
        if signal['action'] != 'HOLD':
            logger.info(f"Entry Price: ${signal['entry_price']:,.2f}")
            logger.info(f"Target Price: ${signal['target_price']:,.2f}")
            logger.info(f"Stop Loss: ${signal['stop_loss']:,.2f}")
            logger.info(f"Potential Profit: {signal['potential_profit_percent']}%")
            logger.info(f"Risk Level: {signal['risk_level']}")
        
        logger.info(f"\nScores:")
        logger.info(f"  Technical: {signal['scores']['technical']}%")
        logger.info(f"  AI Prediction: {signal['scores']['ai_prediction']}%")
        logger.info(f"  Sentiment: {signal['scores']['sentiment']}%")
        
        logger.info(f"\nReasoning:")
        for reason in signal['reasoning']:
            logger.info(f"  • {reason}")
        logger.info(f"{'='*60}\n")
    
    def scan_all_coins(self) -> List[Dict]:
        """Scan all configured coins and return signals"""
        signals = []
        
        for coin in settings.coins_list:
            try:
                signal = self.analyze_coin(coin)
                if signal.get('action') != 'HOLD':
                    signals.append(signal)
            except Exception as e:
                logger.error(f"Error analyzing {coin}: {e}")
        
        # Sort by confidence
        signals.sort(key=lambda x: x['confidence'], reverse=True)
        
        return signals


if __name__ == "__main__":
    # Test signal generator
    generator = AISignalGenerator()
    
    # Analyze BTC
    signal = generator.analyze_coin('BTC', retrain_lstm=True)
    
    # Save signal to file
    with open('/workspace/crypto-ai-trader/data/latest_signal.json', 'w') as f:
        json.dump(signal, f, indent=2)
    
    print("\n✅ Signal saved to data/latest_signal.json")
