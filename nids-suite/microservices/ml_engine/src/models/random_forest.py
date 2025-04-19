#!/usr/bin/env python3
"""
Random Forest model for attack classification
"""

import os
import joblib
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Union, Optional, Tuple
from sklearn.ensemble import RandomForestClassifier

from ..utils import save_model, load_model

logger = logging.getLogger(__name__)

class RandomForestModel:
    """
    Random Forest model for classifying network attacks.
    
    This model classifies detected anomalies into specific attack types,
    providing more actionable information about the nature of the threat.
    """
    
    def __init__(
        self,
        n_estimators: int = 100,
        criterion: str = 'gini',
        max_depth: Optional[int] = None,
        min_samples_split: int = 2,
        min_samples_leaf: int = 1,
        class_weight: Optional[Union[str, Dict]] = 'balanced',
        random_state: int = 42,
        **kwargs
    ):
        """
        Initialize the Random Forest model.
        
        Args:
            n_estimators: The number of trees in the forest
            criterion: The function to measure the quality of a split
            max_depth: The maximum depth of the tree
            min_samples_split: The minimum number of samples required to split an internal node
            min_samples_leaf: The minimum number of samples required to be at a leaf node
            class_weight: Weights associated with classes
            random_state: Random seed for reproducibility
        """
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            criterion=criterion,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            class_weight=class_weight,
            random_state=random_state,
            **kwargs
        )
        
        self.feature_names = []
        self.class_names = []
        self.is_fitted = False
        logger.debug("Random Forest model initialized")
    
    def train(self, X: Union[np.ndarray, pd.DataFrame, List[Dict]], y: Union[np.ndarray, pd.Series, List]) -> 'RandomForestModel':
        """
        Train the Random Forest model.
        
        Args:
            X: Training data features
            y: Training data labels (attack types)
            
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
            self.model.fit(X, y)
            self.is_fitted = True
            
            # Save class names
            self.class_names = self.model.classes_.tolist() if hasattr(self.model, 'classes_') else []
            
            logger.info(f"Random Forest model trained on {len(X)} samples with {X.shape[1]} features and {len(self.class_names)} classes")
            return self
            
        except Exception as e:
            logger.error(f"Error training Random Forest model: {str(e)}")
            raise
    
    def predict(self, X: Union[np.ndarray, pd.DataFrame, List[Dict]]) -> np.ndarray:
        """
        Predict attack classes for input samples.
        
        Args:
            X: Input data
            
        Returns:
            np.ndarray: Predicted class labels
        """
        try:
            # Convert list of dictionaries to DataFrame if needed
            if isinstance(X, list) and X and isinstance(X[0], dict):
                X = pd.DataFrame(X)
            
            if not self.is_fitted:
                logger.warning("Random Forest model not fitted yet - will return default class")
                return np.array(["normal"] * len(X))
            
            return self.model.predict(X)
            
        except Exception as e:
            logger.error(f"Error predicting with Random Forest model: {str(e)}")
            return np.array(["normal"] * len(X))  # Safe default: assume everything is normal
    
    def predict_proba(self, X: Union[np.ndarray, pd.DataFrame, List[Dict]]) -> np.ndarray:
        """
        Predict class probabilities for input samples.
        
        Args:
            X: Input data
            
        Returns:
            np.ndarray: Predicted class probabilities
        """
        try:
            # Convert list of dictionaries to DataFrame if needed
            if isinstance(X, list) and X and isinstance(X[0], dict):
                X = pd.DataFrame(X)
            
            if not self.is_fitted:
                logger.warning("Random Forest model not fitted yet - will return uniform probabilities")
                n_classes = max(1, len(self.class_names))
                return np.ones((len(X), n_classes)) / n_classes
            
            return self.model.predict_proba(X)
            
        except Exception as e:
            logger.error(f"Error predicting probabilities with Random Forest model: {str(e)}")
            n_classes = max(1, len(self.class_names))
            return np.ones((len(X), n_classes)) / n_classes  # Safe default: uniform probabilities
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance scores.
        
        Returns:
            Dict[str, float]: Dictionary mapping feature names to importance scores
        """
        if not self.is_fitted:
            logger.warning("Model not fitted yet, cannot get feature importance")
            return {}
        
        try:
            importances = self.model.feature_importances_
            
            if len(self.feature_names) != len(importances):
                # If feature names don't match importance array, use generic names
                feature_names = [f"feature_{i}" for i in range(len(importances))]
            else:
                feature_names = self.feature_names
            
            # Create dictionary of feature importances
            importance_dict = {
                name: float(importance)
                for name, importance in zip(feature_names, importances)
            }
            
            # Sort by importance (descending)
            return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
            
        except Exception as e:
            logger.error(f"Error getting feature importance: {str(e)}")
            return {}
    
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
                'class_names': self.class_names,
                'is_fitted': self.is_fitted,
                'model_type': 'RandomForest'
            }
            
            # Save using utility function
            return save_model(model_data, filepath)
            
        except Exception as e:
            logger.error(f"Error saving Random Forest model: {str(e)}")
            return False
    
    def load_model(self, filepath: str) -> bool:
        """
        Load a model from disk.
        
        Args:
            filepath: Path to load the model from
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load model data
            model_data = load_model(filepath)
            
            if model_data is None:
                return False
            
            # Set model attributes
            self.model = model_data['model']
            self.feature_names = model_data.get('feature_names', [])
            self.class_names = model_data.get('class_names', [])
            self.is_fitted = model_data.get('is_fitted', False)
            
            logger.info(f"Random Forest model loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading Random Forest model: {str(e)}")
            return False