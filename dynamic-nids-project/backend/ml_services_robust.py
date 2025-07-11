# backend/ml_services_robust.py

"""
Robust ML Services Implementation for Windows
Handles numpy/pandas compatibility issues and warnings
"""

import warnings
import logging
import os
import sys

# Suppress numpy warnings on Windows
warnings.filterwarnings('ignore', category=RuntimeWarning, module='numpy')
warnings.filterwarnings('ignore', message='.*MINGW-W64.*')
warnings.filterwarnings('ignore', message='.*invalid value encountered.*')

# Configure logging to suppress numpy warnings
logging.getLogger('numpy').setLevel(logging.ERROR)

import asyncio
import json
from typing import Dict, Optional, Any, List
from datetime import datetime

# Try to import ML libraries with better error handling
ML_AVAILABLE = False
PANDAS_AVAILABLE = False
SKLEARN_AVAILABLE = False

try:
    # Test pandas import
    import pandas as pd
    # Test basic pandas functionality
    test_df = pd.DataFrame({'test': [1, 2, 3]})
    PANDAS_AVAILABLE = True
    print(f"[✓] Pandas available (version: {pd.__version__})")
except Exception as e:
    print(f"[!] Pandas not available: {e}")
    PANDAS_AVAILABLE = False

try:
    # Test scikit-learn import
    import sklearn
    from sklearn.ensemble import RandomForestClassifier, IsolationForest
    from sklearn.preprocessing import StandardScaler
    # Test basic sklearn functionality
    test_rf = RandomForestClassifier(n_estimators=2)
    SKLEARN_AVAILABLE = True
    print(f"[✓] Scikit-learn available (version: {sklearn.__version__})")
except Exception as e:
    print(f"[!] Scikit-learn not available: {e}")
    SKLEARN_AVAILABLE = False

try:
    import numpy as np
    import joblib
    # Test basic numpy operations
    test_array = np.array([1, 2, 3])
    test_result = np.mean(test_array)
    print(f"[✓] Numpy available (version: {np.__version__})")
except Exception as e:
    print(f"[!] Numpy not available: {e}")

# Determine ML availability
ML_AVAILABLE = PANDAS_AVAILABLE and SKLEARN_AVAILABLE

# Import fallback detector
try:
    from simple_detector import SimpleAnomalyDetector
    SIMPLE_DETECTOR_AVAILABLE = True
except ImportError:
    SIMPLE_DETECTOR_AVAILABLE = False

class RobustMLServices:
    """
    Robust ML services that handle Windows compatibility issues
    """
    
    def __init__(self, models_dir="models"):
        self.models_dir = models_dir
        self.ml_available = ML_AVAILABLE
        self.models = {}
        self.prediction_history = []
        
        # Ensure models directory exists
        os.makedirs(models_dir, exist_ok=True)
        
        # Initialize appropriate detector
        if self.ml_available:
            self.detector = WindowsCompatibleMLDetector(models_dir)
            print("[*] Advanced ML detector initialized")
        elif SIMPLE_DETECTOR_AVAILABLE:
            self.detector = SimpleAnomalyDetector()
            print("[*] Simple detector initialized")
        else:
            self.detector = BasicRuleDetector()
            print("[*] Basic rule detector initialized")
        
        self.performance_stats = {
            'total_predictions': 0,
            'anomaly_count': 0,
            'error_count': 0
        }
    
    async def predict_anomaly(self, feature_vector: Dict) -> Optional[Dict]:
        """Main prediction interface with error handling"""
        try:
            self.performance_stats['total_predictions'] += 1
            
            result = await self.detector.predict(feature_vector)
            
            if result and result.get('is_anomaly'):
                self.performance_stats['anomaly_count'] += 1
            
            # Store prediction for analysis
            self.prediction_history.append({
                'timestamp': datetime.utcnow().isoformat(),
                'prediction': result
            })
            
            # Keep only recent predictions
            if len(self.prediction_history) > 100:
                self.prediction_history = self.prediction_history[-100:]
            
            return result
            
        except Exception as e:
            self.performance_stats['error_count'] += 1
            logging.error(f"Error in ML prediction: {e}")
            return {
                'is_anomaly': False,
                'confidence': 0.0,
                'error': 'prediction_failed',
                'model_type': 'error_fallback'
            }
    
    def get_model_info(self) -> Dict:
        """Get information about current models"""
        return {
            'ml_available': self.ml_available,
            'pandas_available': PANDAS_AVAILABLE,
            'sklearn_available': SKLEARN_AVAILABLE,
            'model_type': 'Advanced' if self.ml_available else 'Simple',
            'performance_stats': self.performance_stats,
            'prediction_count': len(self.prediction_history)
        }
    
    def get_feature_importance(self) -> Dict:
        """Get feature importance from models"""
        if hasattr(self.detector, 'get_feature_importance'):
            return self.detector.get_feature_importance()
        return {'message': 'Feature importance not available in current mode'}


class WindowsCompatibleMLDetector:
    """ML detector optimized for Windows compatibility"""
    
    def __init__(self, models_dir):
        self.models_dir = models_dir
        self.models = {}
        self.feature_columns = [
            'packet_length', 'tcp_flags', 'src_port', 'dst_port'
        ]
        
        # Try to load or create simple models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize models with Windows-safe operations"""
        try:
            # Try to load existing models
            rf_path = os.path.join(self.models_dir, 'rf_model.joblib')
            if_path = os.path.join(self.models_dir, 'if_model.joblib')
            
            if os.path.exists(rf_path) and os.path.exists(if_path):
                self.models['random_forest'] = joblib.load(rf_path)
                self.models['isolation_forest'] = joblib.load(if_path)
                print("[*] Existing models loaded")
            else:
                # Create simple models with Windows-safe parameters
                self._create_safe_models()
                
        except Exception as e:
            print(f"[!] Model initialization failed: {e}")
            self._create_safe_models()
    
    def _create_safe_models(self):
        """Create models with Windows-safe parameters"""
        try:
            # Create synthetic data with Windows-safe operations
            training_data = []
            for i in range(100):  # Smaller dataset for safety
                if i < 80:  # Normal traffic
                    sample = {
                        'packet_length': 500 + (i % 100),
                        'tcp_flags': 18 if i % 2 == 0 else 24,
                        'src_port': 80 if i % 3 == 0 else 443,
                        'dst_port': 1024 + (i % 1000),
                        'label': 0
                    }
                else:  # Anomalous traffic
                    sample = {
                        'packet_length': 1500 + (i % 500),
                        'tcp_flags': 49 + (i % 10),
                        'src_port': 1337 + (i % 100),
                        'dst_port': 6666 + (i % 100),
                        'label': 1
                    }
                training_data.append(sample)
            
            # Convert to DataFrame
            df = pd.DataFrame(training_data)
            X = df[self.feature_columns]
            y = df['label']
            
            # Create simple models with minimal parameters
            rf_model = RandomForestClassifier(
                n_estimators=10,  # Small number for Windows safety
                max_depth=5,
                random_state=42,
                n_jobs=1  # Single thread for Windows compatibility
            )
            rf_model.fit(X, y)
            
            if_model = IsolationForest(
                n_estimators=10,  # Small number for Windows safety
                contamination=0.2,
                random_state=42,
                n_jobs=1  # Single thread for Windows compatibility
            )
            if_model.fit(X)
            
            # Save models
            self.models['random_forest'] = rf_model
            self.models['isolation_forest'] = if_model
            
            joblib.dump(rf_model, os.path.join(self.models_dir, 'rf_model.joblib'))
            joblib.dump(if_model, os.path.join(self.models_dir, 'if_model.joblib'))
            
            print("[*] Safe models created and saved")
            
        except Exception as e:
            print(f"[!] Safe model creation failed: {e}")
            # Use basic detection as fallback
            self.models = {}
    
    async def predict(self, feature_vector):
        """Predict with Windows-safe operations"""
        if not self.models:
            return self._basic_rule_prediction(feature_vector)
        
        try:
            # Prepare data
            data = {col: [feature_vector.get(col, 0)] for col in self.feature_columns}
            df = pd.DataFrame(data)
            
            results = {
                'predictions': {},
                'is_anomaly': False,
                'confidence': 0.0,
                'model_type': 'advanced_ml'
            }
            
            # Random Forest prediction
            if 'random_forest' in self.models:
                rf_pred = self.models['random_forest'].predict(df)[0]
                rf_proba = self.models['random_forest'].predict_proba(df)[0]
                
                results['predictions']['random_forest'] = int(rf_pred)
                results['confidence'] = float(max(rf_proba))
                
                if rf_pred == 1:
                    results['is_anomaly'] = True
            
            # Isolation Forest prediction
            if 'isolation_forest' in self.models:
                if_pred = self.models['isolation_forest'].predict(df)[0]
                
                results['predictions']['isolation_forest'] = int(if_pred)
                
                if if_pred == -1:  # Isolation Forest anomaly
                    results['is_anomaly'] = True
            
            return results
            
        except Exception as e:
            logging.error(f"ML prediction error: {e}")
            return self._basic_rule_prediction(feature_vector)
    
    def _basic_rule_prediction(self, feature_vector):
        """Fallback rule-based prediction"""
        anomaly_score = 0
        
        # Large packet check
        if feature_vector.get('packet_length', 0) > 1400:
            anomaly_score += 0.3
        
        # Suspicious port check
        suspicious_ports = {1337, 4444, 6666, 31337}
        if (feature_vector.get('src_port') in suspicious_ports or 
            feature_vector.get('dst_port') in suspicious_ports):
            anomaly_score += 0.5
        
        # Unusual TCP flags
        tcp_flags = feature_vector.get('tcp_flags', 0)
        if tcp_flags > 63 or tcp_flags in {4, 49}:  # RST or unusual combinations
            anomaly_score += 0.4
        
        return {
            'is_anomaly': anomaly_score > 0.5,
            'confidence': min(anomaly_score, 1.0),
            'model_type': 'rule_based_fallback',
            'anomaly_score': anomaly_score
        }
    
    def get_feature_importance(self):
        """Get feature importance if available"""
        if 'random_forest' in self.models:
            try:
                importances = self.models['random_forest'].feature_importances_
                return dict(zip(self.feature_columns, [float(x) for x in importances]))
            except:
                pass
        return {'message': 'Feature importance not available'}


class BasicRuleDetector:
    """Ultra-basic rule detector as final fallback"""
    
    async def predict(self, feature_vector):
        """Basic rule-based detection"""
        anomaly_score = 0
        
        # Simple checks without external dependencies
        packet_length = feature_vector.get('packet_length', 0)
        src_port = feature_vector.get('src_port', 0)
        dst_port = feature_vector.get('dst_port', 0)
        
        if packet_length > 1400:
            anomaly_score += 0.3
        
        if src_port in [1337, 4444, 6666] or dst_port in [1337, 4444, 6666]:
            anomaly_score += 0.6
        
        if packet_length < 64 and packet_length > 0:
            anomaly_score += 0.2
        
        return {
            'is_anomaly': anomaly_score > 0.5,
            'confidence': min(anomaly_score, 1.0),
            'model_type': 'basic_rules',
            'anomaly_score': anomaly_score
        }


# Global robust ML services instance
robust_ml_services = None

def get_robust_ml_services():
    """Get or create global robust ML services instance"""
    global robust_ml_services
    if robust_ml_services is None:
        robust_ml_services = RobustMLServices()
    return robust_ml_services

# Convenience function
async def robust_predict_anomaly(feature_vector):
    """Robust anomaly prediction function"""
    services = get_robust_ml_services()
    return await services.predict_anomaly(feature_vector)
