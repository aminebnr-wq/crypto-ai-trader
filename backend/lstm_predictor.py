"""
LSTM Neural Network for Price Prediction
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import joblib
import os
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class LSTMPricePredictor:
    """LSTM model for cryptocurrency price prediction"""
    
    def __init__(self, lookback: int = 60, forecast_steps: int = 24):
        """
        Initialize LSTM predictor
        
        Args:
            lookback: Number of historical time steps to use
            forecast_steps: Number of steps ahead to forecast
        """
        self.lookback = lookback
        self.forecast_steps = forecast_steps
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.is_trained = False
        
    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for LSTM training
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            X, y arrays for training
        """
        # Use multiple features
        features = ['close', 'volume', 'high', 'low']
        data = df[features].values
        
        # Scale data
        scaled_data = self.scaler.fit_transform(data)
        
        X, y = [], []
        
        for i in range(self.lookback, len(scaled_data) - self.forecast_steps):
            X.append(scaled_data[i-self.lookback:i])
            y.append(scaled_data[i + self.forecast_steps - 1, 0])  # Predict close price
        
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape: Tuple) -> Sequential:
        """Build LSTM model architecture"""
        model = Sequential([
            # First LSTM layer
            LSTM(units=128, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            
            # Second LSTM layer
            LSTM(units=64, return_sequences=True),
            Dropout(0.2),
            
            # Third LSTM layer
            LSTM(units=32, return_sequences=False),
            Dropout(0.2),
            
            # Dense layers
            Dense(units=16, activation='relu'),
            Dense(units=1)  # Output: predicted price
        ])
        
        model.compile(
            optimizer='adam',
            loss='mean_squared_error',
            metrics=['mae', 'mse']
        )
        
        return model
    
    def train(
        self,
        df: pd.DataFrame,
        epochs: int = 50,
        batch_size: int = 32,
        validation_split: float = 0.2
    ) -> Dict:
        """
        Train the LSTM model
        
        Args:
            df: DataFrame with historical data
            epochs: Number of training epochs
            batch_size: Batch size for training
            validation_split: Validation data split ratio
            
        Returns:
            Training history
        """
        logger.info("📊 Preparing data for LSTM training...")
        X, y = self.prepare_data(df)
        
        if len(X) < 100:
            logger.error("❌ Not enough data for training. Need at least 100 samples.")
            return {}
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, shuffle=False
        )
        
        logger.info(f"📊 Training set: {X_train.shape}, Validation set: {X_val.shape}")
        
        # Build model
        self.model = self.build_model(input_shape=(X_train.shape[1], X_train.shape[2]))
        
        logger.info(f"🤖 Model architecture:\n{self.model.summary()}")
        
        # Early stopping
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        # Train
        logger.info("🚀 Starting LSTM training...")
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_val, y_val),
            callbacks=[early_stop],
            verbose=1
        )
        
        self.is_trained = True
        logger.info("✅ LSTM training completed!")
        
        return {
            'final_loss': history.history['loss'][-1],
            'final_val_loss': history.history['val_loss'][-1],
            'epochs_trained': len(history.history['loss'])
        }
    
    def predict(self, df: pd.DataFrame) -> Dict:
        """
        Make price predictions
        
        Args:
            df: Recent historical data
            
        Returns:
            Prediction results with confidence
        """
        if not self.is_trained or self.model is None:
            logger.error("❌ Model not trained yet!")
            return {'error': 'Model not trained'}
        
        # Prepare recent data
        features = ['close', 'volume', 'high', 'low']
        recent_data = df[features].tail(self.lookback).values
        
        # Scale
        scaled_data = self.scaler.transform(recent_data)
        
        # Reshape for prediction
        X_pred = np.array([scaled_data])
        
        # Predict
        prediction_scaled = self.model.predict(X_pred, verbose=0)
        
        # Inverse transform to get actual price
        # Create dummy array with same shape as original features
        dummy = np.zeros((1, len(features)))
        dummy[0, 0] = prediction_scaled[0, 0]
        predicted_price = self.scaler.inverse_transform(dummy)[0, 0]
        
        current_price = df['close'].iloc[-1]
        price_change = ((predicted_price - current_price) / current_price) * 100
        
        # Calculate prediction confidence based on recent model performance
        confidence = self._calculate_confidence(df, predicted_price)
        
        return {
            'predicted_price': predicted_price,
            'current_price': current_price,
            'price_change_percent': price_change,
            'direction': 'up' if price_change > 0 else 'down',
            'confidence': confidence,
            'forecast_hours': self.forecast_steps
        }
    
    def _calculate_confidence(self, df: pd.DataFrame, predicted_price: float) -> float:
        """
        Calculate prediction confidence based on historical accuracy
        
        Returns:
            Confidence score (0-100)
        """
        # Simple confidence calculation based on price volatility
        recent_prices = df['close'].tail(self.lookback)
        volatility = recent_prices.std() / recent_prices.mean()
        
        # Lower volatility = higher confidence
        base_confidence = max(50, min(90, 90 - (volatility * 1000)))
        
        # Adjust based on prediction magnitude
        current_price = df['close'].iloc[-1]
        change_magnitude = abs((predicted_price - current_price) / current_price)
        
        # Penalize extreme predictions
        if change_magnitude > 0.1:  # >10% change
            base_confidence *= 0.7
        elif change_magnitude > 0.05:  # >5% change
            base_confidence *= 0.85
        
        return min(95, max(50, base_confidence))
    
    def save_model(self, model_path: str, scaler_path: str):
        """Save trained model and scaler"""
        if self.model:
            self.model.save(model_path)
            joblib.dump(self.scaler, scaler_path)
            logger.info(f"✅ Model saved to {model_path}")
    
    def load_model(self, model_path: str, scaler_path: str):
        """Load trained model and scaler"""
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            self.model = load_model(model_path)
            self.scaler = joblib.load(scaler_path)
            self.is_trained = True
            logger.info(f"✅ Model loaded from {model_path}")
        else:
            logger.error(f"❌ Model files not found!")


if __name__ == "__main__":
    # Test LSTM predictor
    from binance_client import BinanceDataFetcher
    
    fetcher = BinanceDataFetcher()
    df = fetcher.get_historical_data('BTC', interval='1h', days=60)
    
    print(f"\n📊 Data shape: {df.shape}")
    
    # Create and train predictor
    predictor = LSTMPricePredictor(lookback=60, forecast_steps=24)
    
    print("\n🤖 Training LSTM model...")
    history = predictor.train(df, epochs=20, batch_size=32)
    print(f"\n✅ Training complete: {history}")
    
    # Make prediction
    print("\n🔮 Making prediction...")
    prediction = predictor.predict(df)
    print(f"\n📈 Prediction Results:")
    print(f"Current Price: ${prediction['current_price']:,.2f}")
    print(f"Predicted Price: ${prediction['predicted_price']:,.2f}")
    print(f"Change: {prediction['price_change_percent']:.2f}%")
    print(f"Direction: {prediction['direction']}")
    print(f"Confidence: {prediction['confidence']:.2f}%")
