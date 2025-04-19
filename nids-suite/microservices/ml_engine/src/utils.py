#!/usr/bin/env python3
"""
Utility functions for the ML Engine
"""

import os
import joblib
import logging
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional, Union
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

logger = logging.getLogger(__name__)

def calculate_metrics(y_true: List, y_pred: List) -> Dict[str, float]:
    """
    Calculate performance metrics for classification.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        
    Returns:
        Dictionary of metrics
    """
    try:
        metrics = {
            'accuracy': float(accuracy_score(y_true, y_pred)),
            'precision': float(precision_score(y_true, y_pred, average='weighted', zero_division=0)),
            'recall': float(recall_score(y_true, y_pred, average='weighted', zero_division=0)),
            'f1_score': float(f1_score(y_true, y_pred, average='weighted', zero_division=0))
        }
        
        # Add confusion matrix as list of lists
        cm = confusion_matrix(y_true, y_pred)
        metrics['confusion_matrix'] = cm.tolist()
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error calculating metrics: {str(e)}")
        return {
            'accuracy': 0.0,
            'precision': 0.0,
            'recall': 0.0,
            'f1_score': 0.0,
            'error': str(e)
        }

def save_model(model: Any, filepath: str) -> bool:
    """
    Save a model to disk.
    
    Args:
        model: The model to save
        filepath: Path to save the model
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save model
        joblib.dump(model, filepath)
        logger.info(f"Model saved to {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving model: {str(e)}")
        return False

def load_model(filepath: str) -> Any:
    """
    Load a model from disk.
    
    Args:
        filepath: Path to the model file
        
    Returns:
        The loaded model or None if failed
    """
    try:
        if not os.path.exists(filepath):
            logger.error(f"Model file not found: {filepath}")
            return None
            
        model = joblib.load(filepath)
        logger.info(f"Model loaded from {filepath}")
        return model
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return None

def prepare_features(data: Dict[str, Any]) -> Dict[str, float]:
    """
    Prepare features from raw data for model input.
    
    Args:
        data: Raw data dictionary
        
    Returns:
        Dictionary of prepared features
    """
    features = {}
    
    try:
        # Basic flow features
        if 'flow' in data:
            flow = data['flow']
            
            # Extract basic flow stats
            features['bytes'] = float(flow.get('bytes', 0))
            features['packets'] = float(flow.get('packets', 0))
            
            # Calculate derived metrics
            duration = (flow.get('end_time', 0) - flow.get('start_time', 0)) / 1000000  # microseconds to seconds
            features['duration'] = float(max(0.001, duration))  # Avoid division by zero
            
            if features['duration'] > 0:
                features['bytes_per_sec'] = features['bytes'] / features['duration']
                features['packets_per_sec'] = features['packets'] / features['duration']
            
            if features['packets'] > 0:
                features['bytes_per_packet'] = features['bytes'] / features['packets']
            
            # Protocol encoding (one-hot)
            protocol = flow.get('protocol', '').lower()
            features['is_tcp'] = 1.0 if protocol == 'tcp' else 0.0
            features['is_udp'] = 1.0 if protocol == 'udp' else 0.0
            features['is_icmp'] = 1.0 if protocol == 'icmp' else 0.0
            
            # Port analysis
            src_port = flow.get('src_port', 0)
            dst_port = flow.get('dst_port', 0)
            features['src_port_is_well_known'] = 1.0 if src_port < 1024 else 0.0
            features['dst_port_is_well_known'] = 1.0 if dst_port < 1024 else 0.0
        
        # Feature extraction results
        if 'features' in data:
            extracted = data['features']
            for key, value in extracted.items():
                # Ensure we only use numeric features
                try:
                    features[key] = float(value)
                except (ValueError, TypeError):
                    pass
    
    except Exception as e:
        logger.error(f"Error preparing features: {str(e)}")
    
    return features

def normalize_features(features: Dict[str, float], means: Dict[str, float] = None, stds: Dict[str, float] = None) -> Dict[str, float]:
    """
    Normalize features using mean and standard deviation.
    
    Args:
        features: Dictionary of features
        means: Dictionary of mean values per feature (if None, calculate from features)
        stds: Dictionary of standard deviation values per feature (if None, calculate from features)
        
    Returns:
        Dictionary of normalized features
    """
    normalized = {}
    
    try:
        # If means and stds not provided, use the features as is
        if means is None or stds is None:
            return features
            
        # Normalize each feature
        for key, value in features.items():
            if key in means and key in stds:
                # Avoid division by zero
                std = max(stds[key], 1e-10)
                normalized[key] = (value - means[key]) / std
            else:
                normalized[key] = value
                
    except Exception as e:
        logger.error(f"Error normalizing features: {str(e)}")
        return features
        
    return normalized

def get_timestamp() -> str:
    """Get current timestamp as formatted string"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')