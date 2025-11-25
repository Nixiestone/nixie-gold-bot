import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb
import pickle
import os
import config

class MLSignalFilter:
    def __init__(self):
        self.model = None
        self.feature_names = []
        self.model_path = config.ML_MODEL_PATH
    
    def extract_features(self, df_h4, df_m15, signal_data=None):
        """
        Extract features for ML model
        
        Returns: Feature vector (numpy array)
        """
        try:
            features = []
            
            features.append(df_h4['RSI'].iloc[-1])
            features.append(df_h4['ADX'].iloc[-1])
            features.append(df_h4['MACD'].iloc[-1])
            features.append(df_h4['MACD_diff'].iloc[-1])
            features.append(df_h4['ATR'].iloc[-1])
            features.append(df_h4['Volume_Ratio'].iloc[-1])
            
            features.append(1 if df_h4['EMA_20'].iloc[-1] > df_h4['EMA_50'].iloc[-1] else 0)
            
            bb_position = (df_h4['Close'].iloc[-1] - df_h4['BB_lower'].iloc[-1]) / \
                         (df_h4['BB_upper'].iloc[-1] - df_h4['BB_lower'].iloc[-1])
            features.append(bb_position)
            
            features.append(df_m15['RSI'].iloc[-1])
            features.append(df_m15['Stoch_K'].iloc[-1])
            features.append(df_m15['Stoch_D'].iloc[-1])
            features.append(df_m15['MACD_diff'].iloc[-1])
            features.append(df_m15['Volume_Ratio'].iloc[-1])
            
            stoch_cross = 1 if df_m15['Stoch_K'].iloc[-1] > df_m15['Stoch_D'].iloc[-1] else 0
            features.append(stoch_cross)
            
            price_momentum = (df_m15['Close'].iloc[-1] - df_m15['Close'].iloc[-6]) / df_m15['Close'].iloc[-6]
            features.append(price_momentum)
            
            volatility_pct = df_m15['ATR'].iloc[-1] / df_m15['Close'].iloc[-1]
            features.append(volatility_pct)
            
            if signal_data:
                features.append(signal_data.get('confidence', 50) / 100)
                features.append(signal_data.get('pips_risk', 20) / 30)
                features.append(signal_data.get('rr_ratio', 1.5) / 4.0)
                features.append(1 if signal_data.get('signal') == 'LONG' else 0)
            
            return np.array(features).reshape(1, -1)
            
        except Exception as e:
            print(f"[ERROR] Error extracting features: {e}")
            return None
    
    def train_model(self, historical_data, labels):
        """
        Train the ML model
        
        Args:
            historical_data: DataFrame with features
            labels: Array of outcomes (1 = win, 0 = loss)
        """
        try:
            print(" Training ML model...")
            
            X_train, X_test, y_train, y_test = train_test_split(
                historical_data, labels, test_size=0.2, random_state=42
            )
            
            self.model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
            
            self.model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            print(f" Model trained! Accuracy: {accuracy:.2%}")
            print("\n Classification Report:")
            print(classification_report(y_test, y_pred))
            
            self.save_model()
            
            return accuracy
            
        except Exception as e:
            print(f" Error training model: {e}")
            return 0
    
    def predict(self, features):
        """
        Predict if signal is likely to be profitable
        
        Returns: (prediction, probability)
        """
        try:
            if self.model is None:
                self.load_model()
            
            if self.model is None:
                return 1, 0.5
            
            prediction = self.model.predict(features)[0]
            probability = self.model.predict_proba(features)[0]
            
            return prediction, probability[1]  
            
        except Exception as e:
            print(f" Error making prediction: {e}")
            return 1, 0.5  
    
    def should_take_signal(self, df_h4, df_m15, signal_data):
        """
        Determine if signal passes ML filter
        
        Returns: (bool, confidence)
        """
        try:
            if not config.USE_ML_FILTER:
                return True, 1.0
            
            features = self.extract_features(df_h4, df_m15, signal_data)
            if features is None:
                return True, 0.5  
            
            prediction, probability = self.predict(features)
            
            passes = probability >= config.ML_CONFIDENCE_THRESHOLD
            
            if passes:
                print(f" ML Filter: PASS (Confidence: {probability:.2%})")
            else:
                print(f" ML Filter: FAIL (Confidence: {probability:.2%} < {config.ML_CONFIDENCE_THRESHOLD:.2%})")
            
            return passes, probability
            
        except Exception as e:
            print(f" Error in ML filter: {e}")
            return True, 0.5  
    
    def save_model(self):
        """Save trained model to disk"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
            print(f"Model saved to {self.model_path}")
        except Exception as e:
            print(f" Error saving model: {e}")
    
    def load_model(self):
        """Load trained model from disk"""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                print(f" Model loaded from {self.model_path}")
                return True
            else:
                print(f"  No trained model found at {self.model_path}")
                return False
        except Exception as e:
            print(f" Error loading model: {e}")
            return False
    
    def train_from_real_trades(self):
        """
        Train model using real trade outcomes from trade logger
        """
        try:
            from models.trade_logger import TradeLogger
            
            print(" Training from real trade data...")
            
            logger = TradeLogger()
            X, y = logger.get_training_data()
            
            if X is None or len(X) < 20:
                print("  Not enough trades yet. Need at least 20 completed trades.")
                print("   Continue trading and collecting data!")
                return False
            
            accuracy = self.train_model(X, y)
            
            if accuracy > 0.6:
                print(f" Model trained successfully! Accuracy: {accuracy:.2%}")
                return True
            else:
                print(f"  Model accuracy too low: {accuracy:.2%}")
                print("   Collect more trades for better performance")
                return False
                
        except Exception as e:
            print(f" Error training from real trades: {e}")
            return False
        """
        Generate synthetic training data from historical patterns
        This is a placeholder - you'd replace with real labeled data
        """
        print(f" Generating {num_samples} training samples...")
        
        features_list = []
        labels_list = []
        
        for i in range(num_samples):
            df_h4 = handler.get_gold_data('H4', 200)
            df_m15 = handler.get_gold_data('M15', 500)
            
            if df_h4 is None or df_m15 is None:
                continue
            
            from indicators.technical import TechnicalIndicators
            tech = TechnicalIndicators()
            df_h4 = tech.calculate_all(df_h4)
            df_m15 = tech.calculate_all(df_m15)
            
            features = self.extract_features(df_h4, df_m15)
            if features is not None:
                features_list.append(features[0])
                
                rsi = df_m15['RSI'].iloc[-1]
                label = 1 if (rsi < 35 or rsi > 65) else 0
                labels_list.append(label)
            
            if i % 50 == 0:
                print(f"  Progress: {i}/{num_samples}")
        
        return np.array(features_list), np.array(labels_list)


if __name__ == "__main__":
    print(" Testing ML Signal Filter...")
    
    ml_filter = MLSignalFilter()
    
    if ml_filter.load_model():
        print(" Model loaded successfully")
    else:
        print("  No model found. You can train one using historical data.")
    
    print("\nTo train a model, collect historical trade data with outcomes,")
    print("   then use ml_filter.train_model(features, labels)")