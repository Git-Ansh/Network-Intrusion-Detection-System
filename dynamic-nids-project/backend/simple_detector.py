# backend/simple_detector.py - ML detector with fallbacks for Python 3.13

import json
import random
import time
import numpy as np

class SimpleAnomalyDetector:
    """
    A simplified anomaly detector that works without scikit-learn.
    Uses statistical methods and rule-based detection.
    """
    
    def __init__(self):
        self.packet_history = []
        self.baseline_stats = {
            'avg_packet_size': 500,
            'std_packet_size': 200,
            'common_ports': {80, 443, 22, 53, 25, 110, 143, 993, 995},
            'suspicious_ports': {1337, 4444, 6666, 31337, 12345}
        }
        print("[*] Simple Anomaly Detector initialized (no ML dependencies)")
    
    async def predict(self, feature_vector):
        """
        Analyze a packet and return anomaly prediction using simple rules.
        
        Args:
            feature_vector (dict): Packet features
            
        Returns:
            dict: Prediction results
        """
        if not feature_vector:
            return None
            
        # Store packet for statistical analysis
        self.packet_history.append(feature_vector)
        if len(self.packet_history) > 1000:  # Keep only recent packets
            self.packet_history = self.packet_history[-1000:]
        
        # Rule-based anomaly detection
        anomaly_score = 0
        anomaly_reasons = []
        
        # 1. Check packet size anomalies
        packet_size = feature_vector.get('packet_length', 0)
        if packet_size > 1400:  # Unusually large packet
            anomaly_score += 0.3
            anomaly_reasons.append("Large packet size")
        elif packet_size < 20:  # Unusually small packet
            anomaly_score += 0.2
            anomaly_reasons.append("Small packet size")
        
        # 2. Check for suspicious ports
        src_port = feature_vector.get('src_port', 0)
        dst_port = feature_vector.get('dst_port', 0)
        
        if src_port in self.baseline_stats['suspicious_ports'] or dst_port in self.baseline_stats['suspicious_ports']:
            anomaly_score += 0.5
            anomaly_reasons.append("Suspicious port usage")
        
        # 3. Check for uncommon port combinations
        if src_port > 49152 and dst_port > 49152:  # Both high ports
            anomaly_score += 0.2
            anomaly_reasons.append("Unusual port combination")
        
        # 4. TCP flags analysis
        tcp_flags = feature_vector.get('tcp_flags', 0)
        if tcp_flags == 0:  # No flags set
            anomaly_score += 0.1
        elif tcp_flags & 0x29:  # FIN + URG + PSH combination (unusual)
            anomaly_score += 0.4
            anomaly_reasons.append("Suspicious TCP flags")
        
        # 5. Time-based anomalies (simple approach)
        current_time = time.time()
        if len(self.packet_history) > 10:
            recent_packets = [p for p in self.packet_history[-10:] 
                            if current_time - p.get('timestamp', 0) < 1.0]
            if len(recent_packets) > 8:  # High packet rate
                anomaly_score += 0.3
                anomaly_reasons.append("High packet rate")
        
        # 6. Statistical analysis (simplified)
        if len(self.packet_history) > 50:
            recent_sizes = [p.get('packet_length', 0) for p in self.packet_history[-50:]]
            avg_size = sum(recent_sizes) / len(recent_sizes)
            
            if abs(packet_size - avg_size) > (2 * self.baseline_stats['std_packet_size']):
                anomaly_score += 0.2
                anomaly_reasons.append("Statistical outlier")
        
        # Determine if it's an anomaly
        is_anomaly = anomaly_score > 0.5
        
        # Simulate different model predictions
        rf_prediction = 1 if anomaly_score > 0.6 else 0
        rf_probability = min(anomaly_score, 1.0)
        
        # Isolation Forest simulation (inverted scoring)
        if_score = 1.0 - anomaly_score  # Higher score = more normal
        if_prediction = -1 if anomaly_score > 0.4 else 1
        
        return {
            'rf_prediction': rf_prediction,
            'rf_probability': rf_probability,
            'if_score': if_score,
            'if_prediction': if_prediction,
            'is_anomaly': is_anomaly,
            'anomaly_score': anomaly_score,
            'reasons': anomaly_reasons,
            'method': 'rule_based'
        }

class AdvancedAnomalyDetector:
    """
    Enhanced detector that tries to use scikit-learn if available,
    falls back to simple detection otherwise.
    """
    
    def __init__(self):
        self.use_ml = False
        self.rf_model = None
        self.if_model = None
        self.simple_detector = SimpleAnomalyDetector()
        
        # Try to initialize ML models
        try:
            self._init_ml_models()
        except ImportError as e:
            print(f"[!] ML libraries not available: {e}")
            print("[*] Using rule-based detection instead")
        except Exception as e:
            print(f"[!] Failed to initialize ML models: {e}")
            print("[*] Using rule-based detection instead")
    
    def _init_ml_models(self):
        """Try to initialize scikit-learn models"""
        try:
            from sklearn.ensemble import RandomForestClassifier, IsolationForest
            import joblib
            import os
            
            # Try to load pre-trained models
            if os.path.exists('models/rf_model.joblib') and os.path.exists('models/if_model.joblib'):
                self.rf_model = joblib.load('models/rf_model.joblib')
                self.if_model = joblib.load('models/if_model.joblib')
                self.use_ml = True
                print("[*] ML models loaded successfully")
            else:
                print("[!] Pre-trained models not found, training new ones...")
                self._train_simple_models()
                
        except ImportError:
            raise ImportError("scikit-learn not available")
    
    def _train_simple_models(self):
        """Train simple models with synthetic data"""
        from sklearn.ensemble import RandomForestClassifier, IsolationForest
        import numpy as np
        import joblib
        import os
        
        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 1000
        
        # Normal traffic features
        normal_data = np.column_stack([
            np.random.normal(500, 100, n_samples // 2),  # packet_length
            np.random.choice([2, 18, 24], n_samples // 2),  # tcp_flags (SYN, SYN-ACK, ACK)
            np.random.choice([80, 443, 22, 53], n_samples // 2),  # src_port
            np.random.choice([1024, 2048, 3000, 4000], n_samples // 2)  # dst_port
        ])
        
        # Anomalous traffic features
        anomaly_data = np.column_stack([
            np.random.choice([32, 1500, 2000], n_samples // 2),  # unusual packet sizes
            np.random.choice([4, 49, 63], n_samples // 2),  # unusual flags
            np.random.choice([1337, 4444, 31337], n_samples // 2),  # suspicious ports
            np.random.choice([1337, 6666, 12345], n_samples // 2)  # suspicious ports
        ])
        
        # Combine data
        X = np.vstack([normal_data, anomaly_data])
        y = np.hstack([np.zeros(n_samples // 2), np.ones(n_samples // 2)])
        
        # Train models
        self.rf_model = RandomForestClassifier(n_estimators=50, random_state=42)
        self.rf_model.fit(X, y)
        
        self.if_model = IsolationForest(contamination=0.3, random_state=42)
        self.if_model.fit(normal_data)  # Train only on normal data
        
        # Save models
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.rf_model, 'models/rf_model.joblib')
        joblib.dump(self.if_model, 'models/if_model.joblib')
        
        self.use_ml = True
        print("[*] New ML models trained and saved")
    
    def _preprocess_for_ml(self, feature_vector):
        """Convert feature vector to ML format"""
        import numpy as np
        
        features = [
            feature_vector.get('packet_length', 0),
            feature_vector.get('tcp_flags', 0),
            feature_vector.get('src_port', 0),
            feature_vector.get('dst_port', 0)
        ]
        return np.array(features).reshape(1, -1)
    
    async def predict(self, feature_vector):
        """
        Predict using ML models if available, otherwise use simple detection
        """
        if self.use_ml and self.rf_model and self.if_model:
            try:
                # Use ML models
                X = self._preprocess_for_ml(feature_vector)
                
                rf_prediction = self.rf_model.predict(X)[0]
                rf_probability = self.rf_model.predict_proba(X)[0]
                
                if_score = self.if_model.decision_function(X)[0]
                if_prediction = self.if_model.predict(X)[0]
                
                return {
                    'rf_prediction': int(rf_prediction),
                    'rf_probability': float(rf_probability[1]) if len(rf_probability) > 1 else float(rf_probability[0]),
                    'if_score': float(if_score),
                    'if_prediction': int(if_prediction),
                    'is_anomaly': bool(rf_prediction == 1 or if_prediction == -1),
                    'method': 'ml_models'
                }
            except Exception as e:
                print(f"[!] ML prediction failed: {e}, falling back to simple detection")
                return await self.simple_detector.predict(feature_vector)
        else:
            # Use simple rule-based detection
            return await self.simple_detector.predict(feature_vector)
