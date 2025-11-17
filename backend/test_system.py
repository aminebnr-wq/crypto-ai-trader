"""
Quick Test Script - Run this to verify everything works
"""
import sys
import os

print("=" * 60)
print("🧪 AI Crypto Trading System - Quick Test")
print("=" * 60)

# Test 1: Check Python version
print("\n1️⃣ Checking Python version...")
python_version = sys.version_info
if python_version.major == 3 and python_version.minor >= 9:
    print(f"   ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
else:
    print(f"   ❌ Python {python_version.major}.{python_version.minor} (Need 3.9+)")
    sys.exit(1)

# Test 2: Check .env file
print("\n2️⃣ Checking .env file...")
if os.path.exists('.env'):
    print("   ✅ .env file exists")
    from config import settings
    if settings.BINANCE_API_KEY and settings.BINANCE_SECRET_KEY:
        print("   ✅ API keys configured")
    else:
        print("   ⚠️  API keys not set in .env")
else:
    print("   ❌ .env file not found")
    print("   📝 Run: cp ../.env.example .env")
    sys.exit(1)

# Test 3: Check dependencies
print("\n3️⃣ Checking dependencies...")
required_packages = [
    'fastapi', 'uvicorn', 'pandas', 'numpy',
    'binance', 'tensorflow', 'scikit-learn',
    'ta', 'requests'
]

missing_packages = []
for package in required_packages:
    try:
        __import__(package)
        print(f"   ✅ {package}")
    except ImportError:
        print(f"   ❌ {package} - Not installed")
        missing_packages.append(package)

if missing_packages:
    print(f"\n   ⚠️  Install missing packages:")
    print(f"   pip install -r requirements.txt")
    sys.exit(1)

# Test 4: Test Binance connection
print("\n4️⃣ Testing Binance connection...")
try:
    from binance_client import BinanceDataFetcher
    
    fetcher = BinanceDataFetcher()
    price = fetcher.get_current_price('BTC')
    
    if price > 0:
        print(f"   ✅ Connected to Binance")
        print(f"   💰 BTC Price: ${price:,.2f}")
        
        # Check permissions
        perms = fetcher.check_api_permissions()
        print(f"   🔐 Permissions: {perms}")
        
        if perms.get('can_trade', False):
            print("   ⚠️  WARNING: Trading is enabled on API key!")
            print("   🔒 Recommended: Use Read-Only permissions")
    else:
        print("   ❌ Failed to fetch price")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ Binance connection failed: {e}")
    print("\n   Possible issues:")
    print("   - Check your API keys in .env")
    print("   - Verify internet connection")
    print("   - Check Binance API status")
    sys.exit(1)

# Test 5: Test technical analysis
print("\n5️⃣ Testing technical analysis...")
try:
    from technical_analysis import TechnicalAnalyzer
    
    df = fetcher.get_historical_data('BTC', interval='1h', days=30)
    analyzer = TechnicalAnalyzer(df)
    analyzer.calculate_all_indicators()
    
    print(f"   ✅ Calculated {len(analyzer.df.columns)} indicators")
    
    signal = analyzer.generate_trading_signal()
    print(f"   📊 Signal: {signal['signal']}")
    print(f"   🎯 Confidence: {signal['confidence']:.2f}%")
    
except Exception as e:
    print(f"   ❌ Technical analysis failed: {e}")
    sys.exit(1)

# Test 6: Test news/sentiment
print("\n6️⃣ Testing news & sentiment analysis...")
try:
    from news_sentiment import NewsAnalyzer
    
    news_analyzer = NewsAnalyzer()
    sentiment = news_analyzer.get_coin_sentiment('BTC')
    
    print(f"   ✅ Sentiment: {sentiment['overall_sentiment']}")
    print(f"   📰 News articles: {sentiment['news_count']}")
    
except Exception as e:
    print(f"   ⚠️  Sentiment analysis warning: {e}")
    print("   (This is optional, system will still work)")

# Test 7: Test AI predictor
print("\n7️⃣ Testing LSTM predictor...")
try:
    from lstm_predictor import LSTMPricePredictor
    
    predictor = LSTMPricePredictor(lookback=60, forecast_steps=24)
    print("   ✅ LSTM model initialized")
    print("   ℹ️  Note: Model will train on first use (2-3 min)")
    
except Exception as e:
    print(f"   ❌ LSTM predictor failed: {e}")
    sys.exit(1)

# Test 8: Test signal generator
print("\n8️⃣ Testing signal generator...")
try:
    from signal_generator import AISignalGenerator
    
    generator = AISignalGenerator()
    print("   ✅ Signal generator initialized")
    
except Exception as e:
    print(f"   ❌ Signal generator failed: {e}")
    sys.exit(1)

# Final result
print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\n🚀 System is ready to use!")
print("\nNext steps:")
print("1. Run backend: python main.py")
print("2. Open another terminal and run frontend: cd ../frontend && npm run dev")
print("3. Open browser: http://localhost:3000")
print("\n📖 For detailed guide, read: ../README.md")
print("🚀 Quick start guide: ../docs/QUICK_START.md")
print("\n⚠️  IMPORTANT: Read ../docs/SECURITY.md before going live!")
print("\n" + "=" * 60)
