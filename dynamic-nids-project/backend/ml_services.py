# backend/ml_services.py

"""
ML Services Integration for NIDS
Provides adaptive ML functionality with fallbacks for different environments
"""

import asyncio
import logging
import os
import json
from typing import Dict, Optional, Any, List
from datetime import datetime

# Try to import ML libraries, fall back to simple implementations if not available
ML_AVAILABLE = False
try:
    import pandas as pd
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier, IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    import joblib
    ML_AVAILABLE = True
    print("[*] Full ML libraries available (pandas, scikit-learn)")
except ImportError as e:
    print(f"[!] ML libraries not available: {e}")
    print("[*] Using simplified ML implementation")

# Import our fallback implementations
from simple_detector import SimpleAnomalyDetector

class MLServices:
    """
    Central ML services coordinator that provides:
    1. Anomaly detection with multiple algorithms
    2. Model training and retraining
    3. Feature engineering
    4. Performance monitoring
    5. Adaptive learning
    """
    
    def __init__(self, models_dir="models"):
        self.models_dir = models_dir
        self.ml_available = ML_AVAILABLE
        self.models = {}
        self.model_stats = {}
        self.feature_importance = {}
        self.prediction_history = []
        
        # Ensure models directory exists
        os.makedirs(models_dir, exist_ok=True)
        
        if self.ml_available:
            self.detector = AdvancedMLDetector(models_dir)
        else:
            self.detector = SimpleAnomalyDetector()
            
        self.performance_monitor = PerformanceMonitor()
        
        print(f"[*] ML Services initialized (Advanced: {self.ml_available})")
    
    async def predict_anomaly(self, feature_vector: Dict) -> Optional[Dict]:
        """Main prediction interface"""
        try:
            result = await self.detector.predict(feature_vector)
            
            if result:
                # Store prediction for analysis
                self.prediction_history.append({
                    'timestamp': datetime.utcnow().isoformat(),
                    'features': feature_vector,
                    'prediction': result
                })
                
                # Keep only recent predictions (last 1000)
                if len(self.prediction_history) > 1000:
                    self.prediction_history = self.prediction_history[-1000:]
                
                # Update performance metrics
                self.performance_monitor.update(result, feature_vector)
                
            return result
            
        except Exception as e:
            logging.error(f"Error in ML prediction: {e}")
            return None
    
    async def train_models(self, training_data: Optional[List[Dict]] = None):
        """Train or retrain models"""
        if self.ml_available and hasattr(self.detector, 'train'):
            return await self.detector.train(training_data)
        else:
            print("[!] Model training not available in simple mode")
            return False
    
    def get_model_info(self) -> Dict:
        """Get information about current models"""
        return {
            'ml_available': self.ml_available,
            'model_type': 'Advanced' if self.ml_available else 'Simple',
            'models_loaded': getattr(self.detector, 'models_loaded', 0),
            'prediction_count': len(self.prediction_history),
            'performance_stats': self.performance_monitor.get_stats()
        }
    
    def get_feature_importance(self) -> Dict:
        """Get feature importance from models"""
        if hasattr(self.detector, 'get_feature_importance'):
            return self.detector.get_feature_importance()
        return {}


class AdvancedMLDetector:
    """Advanced ML detector using scikit-learn"""
    
    def __init__(self, models_dir):
        self.models_dir = models_dir
        self.models = {}
        self.scalers = {}
        self.feature_columns = [
            'packet_length', 'tcp_flags', 'src_port', 'dst_port',
            'protocol', 'ttl', 'window_size', 'packet_rate'
        ]
        self.models_loaded = 0
        
        # Load existing models
        self._load_models()
        
        # If no models exist, train basic ones
        if not self.models:
            asyncio.create_task(self._train_default_models())
    
    def _load_models(self):
        """Load pre-trained models from disk"""
        try:
            rf_path = os.path.join(self.models_dir, 'rf_model.joblib')
            if_path = os.path.join(self.models_dir, 'if_model.joblib')
            scaler_path = os.path.join(self.models_dir, 'scaler.joblib')
            
            if os.path.exists(rf_path):
                self.models['random_forest'] = joblib.load(rf_path)
                self.models_loaded += 1
                print("[*] Random Forest model loaded")
            
            if os.path.exists(if_path):
                self.models['isolation_forest'] = joblib.load(if_path)
                self.models_loaded += 1
                print("[*] Isolation Forest model loaded")
            
            if os.path.exists(scaler_path):
                self.scalers['standard'] = joblib.load(scaler_path)
                print("[*] Feature scaler loaded")
                
        except Exception as e:
            print(f"[!] Error loading models: {e}")
    
    async def _train_default_models(self):
        """Train default models with synthetic data"""
        print("[*] Training default ML models...")
        
        # Generate synthetic training data
        training_data = self._generate_synthetic_data(1000)
        
        await self.train(training_data)
    
    def _generate_synthetic_data(self, n_samples=1000):
        """Generate synthetic network traffic data for training"""
        np.random.seed(42)  # For reproducibility
        
        data = []
        for i in range(n_samples):
            # Generate normal traffic (80%)
            if i < n_samples * 0.8:
                feature_vector = {
                    'packet_length': np.random.normal(500, 200),
                    'tcp_flags': np.random.choice([2, 18, 24]),  # SYN, SYN-ACK, ACK
                    'src_port': np.random.choice([80, 443, 22, 53, 25]),
                    'dst_port': np.random.randint(1024, 65536),
                    'protocol': 6,  # TCP
                    'ttl': np.random.randint(60, 255),
                    'window_size': np.random.randint(1024, 65536),
                    'packet_rate': np.random.normal(10, 5),
                    'label': 0  # Normal
                }
            else:
                # Generate anomalous traffic (20%)
                feature_vector = {
                    'packet_length': np.random.choice([32, 1500, 2000]),  # Very small or large
                    'tcp_flags': np.random.choice([4, 49, 63]),  # RST, URG, unusual flags
                    'src_port': np.random.choice([1337, 4444, 6666, 31337]),  # Suspicious ports
                    'dst_port': np.random.choice([1337, 4444, 6666, 31337]),
                    'protocol': np.random.choice([6, 17, 1]),  # TCP, UDP, ICMP
                    'ttl': np.random.choice([1, 255, 128]),  # Unusual TTL
                    'window_size': np.random.choice([0, 1024]),  # Small windows
                    'packet_rate': np.random.normal(100, 50),  # High rate
                    'label': 1  # Anomaly
                }
            
            data.append(feature_vector)
        
        return data
    
    def _preprocess_features(self, feature_vector):
        """Preprocess features for ML models"""
        # Ensure all required features are present
        processed = {}
        for col in self.feature_columns:
            processed[col] = feature_vector.get(col, 0)
        
        # Convert to DataFrame
        df = pd.DataFrame([processed])
        
        # Scale features if scaler is available
        if 'standard' in self.scalers:
            df_scaled = pd.DataFrame(
                self.scalers['standard'].transform(df),
                columns=df.columns
            )
            return df_scaled
        
        return df
    
    async def predict(self, feature_vector):
        """Predict using multiple ML models"""
        if not self.models:
            return None
        
        try:
            # Preprocess features
            processed_data = self._preprocess_features(feature_vector)
            
            results = {
                'predictions': {},
                'scores': {},
                'is_anomaly': False,
                'confidence': 0.0,
                'model_count': len(self.models)
            }
            
            anomaly_votes = 0
            total_confidence = 0
            
            # Random Forest prediction
            if 'random_forest' in self.models:
                rf_pred = self.models['random_forest'].predict(processed_data)[0]
                rf_proba = self.models['random_forest'].predict_proba(processed_data)[0]
                
                results['predictions']['random_forest'] = int(rf_pred)
                results['scores']['rf_probability'] = float(max(rf_proba))
                
                if rf_pred == 1:
                    anomaly_votes += 1
                total_confidence += max(rf_proba)
            
            # Isolation Forest prediction
            if 'isolation_forest' in self.models:
                if_score = self.models['isolation_forest'].decision_function(processed_data)[0]
                if_pred = self.models['isolation_forest'].predict(processed_data)[0]
                
                results['predictions']['isolation_forest'] = int(if_pred)
                results['scores']['if_score'] = float(if_score)
                
                if if_pred == -1:  # Isolation Forest uses -1 for anomalies
                    anomaly_votes += 1
                total_confidence += abs(if_score)
            
            # Ensemble decision
            results['is_anomaly'] = anomaly_votes > 0
            results['confidence'] = total_confidence / len(self.models) if self.models else 0
            
            return results
            
        except Exception as e:
            logging.error(f"Error in advanced ML prediction: {e}")
            return None
    
    async def train(self, training_data):
        """Train models with provided data"""
        if not training_data:
            training_data = self._generate_synthetic_data(1000)
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(training_data)
            
            # Prepare features and labels
            X = df[self.feature_columns]
            y = df['label'] if 'label' in df.columns else [0] * len(df)
            
            # Train scaler
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            X_scaled_df = pd.DataFrame(X_scaled, columns=self.feature_columns)
            
            # Train Random Forest
            rf_model = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                class_weight='balanced'
            )
            rf_model.fit(X_scaled_df, y)
            
            # Train Isolation Forest
            if_model = IsolationForest(
                contamination=0.2,
                random_state=42
            )
            if_model.fit(X_scaled_df)
            
            # Save models
            self.models['random_forest'] = rf_model
            self.models['isolation_forest'] = if_model
            self.scalers['standard'] = scaler
            
            # Save to disk
            joblib.dump(rf_model, os.path.join(self.models_dir, 'rf_model.joblib'))
            joblib.dump(if_model, os.path.join(self.models_dir, 'if_model.joblib'))
            joblib.dump(scaler, os.path.join(self.models_dir, 'scaler.joblib'))
            
            self.models_loaded = len(self.models)
            
            print(f"[*] Models trained successfully ({len(training_data)} samples)")
            return True
            
        except Exception as e:
            logging.error(f"Error training models: {e}")
            return False
    
    def get_feature_importance(self):
        """Get feature importance from Random Forest"""
        if 'random_forest' in self.models:
            importances = self.models['random_forest'].feature_importances_
            return dict(zip(self.feature_columns, importances))
        return {}


class PerformanceMonitor:
    """Monitor ML model performance"""
    
    def __init__(self):
        self.prediction_count = 0
        self.anomaly_count = 0
        self.confidence_scores = []
        self.response_times = []
        
    def update(self, prediction_result, feature_vector):
        """Update performance metrics"""
        self.prediction_count += 1
        
        if prediction_result.get('is_anomaly'):
            self.anomaly_count += 1
        
        confidence = prediction_result.get('confidence', 0)
        self.confidence_scores.append(confidence)
        
        # Keep only recent scores
        if len(self.confidence_scores) > 1000:
            self.confidence_scores = self.confidence_scores[-1000:]
    
    def get_stats(self):
        """Get performance statistics"""
        if not self.confidence_scores:
            return {}
        
        return {
            'total_predictions': self.prediction_count,
            'anomaly_rate': self.anomaly_count / self.prediction_count if self.prediction_count > 0 else 0,
            'avg_confidence': sum(self.confidence_scores) / len(self.confidence_scores),
            'min_confidence': min(self.confidence_scores),
            'max_confidence': max(self.confidence_scores)
        }


# Global ML services instance
ml_services = None

def get_ml_services():
    """Get or create global ML services instance"""
    global ml_services
    if ml_services is None:
        ml_services = MLServices()
    return ml_services

# Convenience functions for easy integration
async def predict_anomaly(feature_vector):
    """Convenient function for anomaly prediction"""
    services = get_ml_services()
    return await services.predict_anomaly(feature_vector)

def get_model_status():
    """Get current model status"""
    services = get_ml_services()
    return services.get_model_info()
