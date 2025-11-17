"""
News and Sentiment Analysis Module
Fetches crypto news and analyzes sentiment
"""
import requests
from datetime import datetime, timedelta
from typing import List, Dict
import logging
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from config import settings

logger = logging.getLogger(__name__)


class NewsAnalyzer:
    """Fetch and analyze crypto news sentiment"""
    
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        self.crypto_keywords = {
            'BTC': ['bitcoin', 'btc'],
            'ETH': ['ethereum', 'eth', 'ether'],
            'BNB': ['binance', 'bnb'],
            'SOL': ['solana', 'sol'],
            'ADA': ['cardano', 'ada']
        }
    
    def fetch_crypto_news(self, coin: str, hours: int = 24) -> List[Dict]:
        """
        Fetch recent news for a cryptocurrency
        
        Args:
            coin: Cryptocurrency symbol (BTC, ETH, etc.)
            hours: Number of hours to look back
        """
        news_items = []
        
        # CryptoPanic API (Free, no key needed for basic usage)
        try:
            url = "https://cryptopanic.com/api/v1/posts/"
            params = {
                'auth_token': 'free',  # Free tier
                'currencies': coin,
                'kind': 'news',
                'filter': 'important'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for item in data.get('results', [])[:10]:
                    news_items.append({
                        'title': item.get('title', ''),
                        'source': item.get('source', {}).get('title', 'Unknown'),
                        'url': item.get('url', ''),
                        'published_at': item.get('published_at', ''),
                        'sentiment': item.get('votes', {}).get('positive', 0) - item.get('votes', {}).get('negative', 0)
                    })
        except Exception as e:
            logger.warning(f"CryptoPanic API error: {e}")
        
        # Fallback: CoinGecko news
        if not news_items:
            try:
                url = f"https://api.coingecko.com/api/v3/coins/{coin.lower()}/news"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get('data', [])[:10]:
                        news_items.append({
                            'title': item.get('title', ''),
                            'source': item.get('source', 'CoinGecko'),
                            'url': item.get('url', ''),
                            'published_at': item.get('published_at', ''),
                            'sentiment': 0
                        })
            except Exception as e:
                logger.warning(f"CoinGecko API error: {e}")
        
        return news_items
    
    def analyze_text_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of text using multiple methods
        
        Returns:
            Dict with compound score, label, and confidence
        """
        # VADER sentiment
        vader_scores = self.vader.polarity_scores(text)
        
        # TextBlob sentiment
        blob = TextBlob(text)
        textblob_polarity = blob.sentiment.polarity
        
        # Combined score
        compound_score = (vader_scores['compound'] + textblob_polarity) / 2
        
        # Determine label
        if compound_score >= 0.2:
            label = 'positive'
            confidence = abs(compound_score) * 100
        elif compound_score <= -0.2:
            label = 'negative'
            confidence = abs(compound_score) * 100
        else:
            label = 'neutral'
            confidence = (1 - abs(compound_score)) * 50
        
        return {
            'score': compound_score,
            'label': label,
            'confidence': min(confidence, 100),
            'vader_compound': vader_scores['compound'],
            'textblob_polarity': textblob_polarity
        }
    
    def get_coin_sentiment(self, coin: str) -> Dict:
        """
        Get overall sentiment for a cryptocurrency
        
        Returns:
            Dict with sentiment analysis and news summary
        """
        news_items = self.fetch_crypto_news(coin, hours=24)
        
        if not news_items:
            return {
                'overall_sentiment': 'neutral',
                'sentiment_score': 0,
                'confidence': 0,
                'news_count': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'recent_news': []
            }
        
        # Analyze each news item
        sentiments = []
        for item in news_items:
            sentiment = self.analyze_text_sentiment(item['title'])
            item['ai_sentiment'] = sentiment
            sentiments.append(sentiment['score'])
        
        # Calculate overall sentiment
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        positive_count = sum(1 for s in sentiments if s > 0.2)
        negative_count = sum(1 for s in sentiments if s < -0.2)
        neutral_count = len(sentiments) - positive_count - negative_count
        
        # Determine overall label
        if avg_sentiment >= 0.2:
            overall_label = 'positive'
        elif avg_sentiment <= -0.2:
            overall_label = 'negative'
        else:
            overall_label = 'neutral'
        
        # Calculate confidence based on consistency
        sentiment_std = np.std(sentiments) if len(sentiments) > 1 else 0
        consistency_score = max(0, 100 - (sentiment_std * 100))
        confidence = (abs(avg_sentiment) * 50 + consistency_score * 50) / 100
        
        return {
            'overall_sentiment': overall_label,
            'sentiment_score': avg_sentiment * 100,  # Scale to -100 to 100
            'confidence': confidence,
            'news_count': len(news_items),
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'recent_news': news_items[:5]  # Top 5 recent news
        }
    
    def check_major_events(self, coin: str) -> List[str]:
        """
        Check for major market events or announcements
        
        Returns:
            List of important events/keywords found
        """
        events = []
        news_items = self.fetch_crypto_news(coin, hours=48)
        
        # Keywords that indicate major events
        major_keywords = [
            'upgrade', 'fork', 'halving', 'sec', 'regulation',
            'partnership', 'acquisition', 'hack', 'exploit',
            'mainnet', 'listing', 'delisting', 'crash', 'surge'
        ]
        
        for item in news_items:
            title_lower = item['title'].lower()
            for keyword in major_keywords:
                if keyword in title_lower:
                    events.append({
                        'keyword': keyword,
                        'title': item['title'],
                        'url': item['url']
                    })
                    break
        
        return events


import numpy as np

if __name__ == "__main__":
    # Test news analyzer
    analyzer = NewsAnalyzer()
    
    print("\n📰 Fetching BTC News and Sentiment...")
    sentiment = analyzer.get_coin_sentiment('BTC')
    
    print(f"\n📊 Overall Sentiment: {sentiment['overall_sentiment']}")
    print(f"Score: {sentiment['sentiment_score']:.2f}")
    print(f"Confidence: {sentiment['confidence']:.2f}%")
    print(f"News Count: {sentiment['news_count']}")
    print(f"Positive: {sentiment['positive_count']} | Negative: {sentiment['negative_count']} | Neutral: {sentiment['neutral_count']}")
    
    print(f"\n📰 Recent News:")
    for news in sentiment['recent_news']:
        print(f"- {news['title']}")
        if 'ai_sentiment' in news:
            print(f"  Sentiment: {news['ai_sentiment']['label']} ({news['ai_sentiment']['score']:.2f})")
    
    # Check major events
    events = analyzer.check_major_events('BTC')
    if events:
        print(f"\n⚠️ Major Events Detected:")
        for event in events[:3]:
            print(f"- [{event['keyword']}] {event['title']}")
