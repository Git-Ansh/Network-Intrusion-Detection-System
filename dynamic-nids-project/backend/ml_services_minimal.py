# backend/ml_services_minimal.py

"""
Minimal ML Services without numpy/sklearn dependencies
Windows-compatible implementation
"""

import asyncio
import logging
import os
import json
from typing import Dict, Optional, Any, List
from datetime import datetime

# Import our numpy-free detector
from simple_detector_nonumpy import SimpleAnomalyDetector

class MLServicesMinimal:
    """
    Minimal ML services coordinator that provides basic anomaly detection
    without heavy ML dependencies for Windows compatibility
    """
    
    def __init__(self, models_dir="models"):
        self.models_dir = models_dir
        self.ml_available = False  # No advanced ML
        self.detector = SimpleAnomalyDetector()
        self.prediction_history = []
        print("[*] Minimal ML Services initialized (Windows-compatible)")
    
    async def predict_anomaly(self, feature_vector: Dict) -> Optional[Dict]:
        """
        Predict anomaly using simple rule-based detection
        
        Args:
            feature_vector: Dictionary of packet features
            
        Returns:
            Dictionary with prediction results
        """
        try:
            if not feature_vector:
                return None
            
            # Use simple detector
            prediction = await self.detector.predict(feature_vector)
            
            # Store prediction history
            self.prediction_history.append({
                'timestamp': datetime.now().isoformat(),
                'features': feature_vector,
                'prediction': prediction
            })
            
            # Keep only recent predictions
            if len(self.prediction_history) > 100:
                self.prediction_history = self.prediction_history[-100:]
            
            return prediction
            
        except Exception as e:
            print(f"[!] Prediction error: {e}")
            return {
                'is_anomaly': False,
                'anomaly_score': 0.0,
                'confidence': 0.0,
                'reasoning': [f'Error: {str(e)}'],
                'detector_type': 'error'
            }
    
    def get_model_info(self) -> Dict:
        """Get information about available models"""
        return {
            'available_models': ['simple_rule_based'],
            'active_model': 'simple_rule_based',
            'ml_available': False,
            'predictions_made': len(self.prediction_history),
            'detector_stats': self.detector.get_stats()
        }
    
    async def train_models(self, training_data: Optional[List[Dict]] = None):
        """Update detector baseline with new data"""
        if training_data:
            self.detector.update_baseline(training_data)
            print(f"[*] Updated detector baseline with {len(training_data)} samples")

def get_ml_services():
    """Get ML services instance"""
    return MLServicesMinimal()

def get_model_status():
    """Get model status"""
    return {
        'models': {
            'simple_detector': {
                'type': 'rule_based',
                'status': 'active',
                'description': 'Simple rule-based anomaly detector'
            }
        },
        'ml_available': False,
        'service_type': 'minimal'
    }
