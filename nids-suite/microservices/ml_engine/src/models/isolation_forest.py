#!/usr/bin/env python3
"""
Isolation Forest model for anomaly detection
"""

import os
import joblib
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Union, Optional
from sklearn.ensemble import IsolationForest

from ..utils import save_model, load_model

logger = logging.getLogger(__name__)

class IsolationForestModel:
    """
    Isolation Forest model for anomaly detection.
    
    This model detects anomalies in network flows by identifying
    data points that are isolated from normal patterns.
    """
    
    def __init__(
        self,
        contamination: float = 0.01,
        n_estimators: int = 100,
        max_samples: str = 'auto',
        max_features: float = 1.0,
        random_state: int = 42,
        **kwargs
    ):
        """
        Initialize the Isolation Forest model.
        
        Args:
            contamination: The proportion of outliers in the data set
            n_estimators: The number of base estimators in the ensemble
            max_samples: The number of samples to draw from X to train each estimator
            max_features: The number of features to draw from X to train each estimator
            random_state: Random seed for reproducibility
        """
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            max_samples=max_samples,
            max_features=max_features,
            random_state=random_state,
            **kwargs
        )
        
        self.feature_names = []
        self.is_fitted = False
        logger.debug("Isolation Forest model initialized")
    
    def fit(self, X: Union[np.ndarray, pd.DataFrame, List[Dict]]) -> 'IsolationForestModel':
        """
        Train the Isolation Forest model.
        
        Args:
            X: Training data, can be a numpy array, pandas DataFrame, or list of dictionaries
            
        Returns:
            self: Trained model
        """
        try:
            # Convert list of dictionaries to DataFrame if needed
            if isinstance(X, list) and X and isinstance(X[0], dict):
                X = pd.DataFrame(X)
                
            # Save feature names if DataFrame
            if isinstance(X, pd.DataFrame):
                self.feature_names = X.columns.tolist()
            
            # Train the model
            self.model.fit(X)
            self.is_fitted = True
            
            logger.info(f"Isolation Forest model trained on {len(X)} samples with {X.shape[1]} features")
            return self
            
        except Exception as e:
            logger.error(f"Error training Isolation Forest model: {str(e)}")
            raise
    
    def predict(self, X: Union[np.ndarray, pd.DataFrame, List[Dict]]) -> np.ndarray:
        """
        Predict whether samples are anomalies or not.
        
        Args:
            X: Input data
            
        Returns:
            np.ndarray: -1 for anomalies, 1 for normal samples
        """
        try:
            # Convert list of dictionaries to DataFrame if needed
            if isinstance(X, list) and X and isinstance(X[0], dict):
                X = pd.DataFrame(X)
            
            if not self.is_fitted:
                logger.warning("Isolation Forest model not fitted yet - will return all normal")
                return np.ones(len(X))
            
            result = self.model.predict(X)
            anomaly_count = np.sum(result == -1)
            
            logger.debug(f"Predicted {anomaly_count} anomalies out of {len(X)} samples")
            return result
            
        except Exception as e:
            logger.error(f"Error predicting with Isolation Forest model: {str(e)}")
            return np.ones(len(X))  # Safe default: assume everything is normal
    
    def decision_function(self, X: Union[np.ndarray, pd.DataFrame, List[Dict]]) -> np.ndarray:
        """
        Compute the anomaly score of samples.
        
        Args:
            X: Input data
            
        Returns:
            np.ndarray: The anomaly score for each sample (lower = more anomalous)
        """
        try:
            # Convert list of dictionaries to DataFrame if needed
            if isinstance(X, list) and X and isinstance(X[0], dict):
                X = pd.DataFrame(X)
            
            if not self.is_fitted:
                logger.warning("Isolation Forest model not fitted yet - will return zeros")
                return np.zeros(len(X))
            
            return self.model.decision_function(X)
            
        except Exception as e:
            logger.error(f"Error computing anomaly scores: {str(e)}")
            return np.zeros(len(X))
    
    def save_model(self, filepath: str) -> bool:
        """
        Save the model to disk.
        
        Args:
            filepath: Path to save the model
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create a dictionary with model and metadata
            model_data = {
                'model': self.model,
                'feature_names': self.feature_names,
                'is_fitted': self.is_fitted,
                'model_type': 'IsolationForest'
            }
            
            # Save using utility function
            return save_model(model_data, filepath)
            
        except Exception as e:
            logger.error(f"Error saving Isolation Forest model: {str(e)}")
            return False
    
    @classmethod
    def load_model(cls, filepath: str) -> Optional['IsolationForestModel']:
        """
        Load a model from disk.
        
        Args:
            filepath: Path to load the model from
            
        Returns:
            Optional[IsolationForestModel]: The loaded model or None if failed
        """
        try:
            # Load model data
            model_data = load_model(filepath)
            
            if model_data is None:
                return None
            
            # Create a new instance
            instance = cls()
            
            # Set model attributes
            instance.model = model_data['model']
            instance.feature_names = model_data.get('feature_names', [])
            instance.is_fitted = model_data.get('is_fitted', False)
            
            logger.info(f"Isolation Forest model loaded from {filepath}")
            return instance
            
        except Exception as e:
            logger.error(f"Error loading Isolation Forest model: {str(e)}")
            return None