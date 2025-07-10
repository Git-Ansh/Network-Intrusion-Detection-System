# backend/detector.py

import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
import os

class AnomalyDetector:
    """
    A class to load and use pre-trained ML models for anomaly detection.
    """
    def __init__(self, rf_model_path='models/rf_model.joblib', if_model_path='models/if_model.joblib'):
        """
        Loads pre-trained Random Forest and Isolation Forest models from specified paths.
        
        Args:
            rf_model_path (str): Path to the saved Random Forest model file.
            if_model_path (str): Path to the saved Isolation Forest model file.
        """
        self.rf_model = None
        self.if_model = None
        
        try:
            self.rf_model = joblib.load(rf_model_path)
            print(f"[*] Random Forest model loaded from {rf_model_path}")
        except FileNotFoundError:
            print(f"[!] Random Forest model file not found at {rf_model_path}. Please run the training script.")
        
        try:
            self.if_model = joblib.load(if_model_path)
            print(f"[*] Isolation Forest model loaded from {if_model_path}")
        except FileNotFoundError:
            print(f"[!] Isolation Forest model file not found at {if_model_path}. Please run the training script.")

        # This feature list must exactly match the features used during model training.
        # It ensures the columns in the DataFrame are in the correct order for prediction.
        self.feature_columns = ['packet_length', 'tcp_flags', 'src_port', 'dst_port']

    def _preprocess(self, feature_vector):
        """
        Prepares a single feature vector for prediction by converting it into a
        DataFrame with the correct column order and data types.
        
        Args:
            feature_vector (dict): A dictionary of features for a single packet.
            
        Returns:
            pd.DataFrame: A DataFrame ready for the Scikit-learn models.
        """
        # Create a DataFrame from the single feature vector.
        # The list comprehension ensures all required features are present, filling with 0 if missing.
        data = {col: [feature_vector.get(col, 0)] for col in self.feature_columns}
        df = pd.DataFrame(data)
        return df[self.feature_columns] # Enforce column order

    async def predict(self, feature_vector):
        """
        Uses the loaded models to score a feature vector and predict if it's an anomaly.
        
        Args:
            feature_vector (dict): The feature vector of the packet to analyze.
            
        Returns:
            dict or None: A dictionary containing prediction results from both models,
                          or None if models are not loaded.
        """
        if not self.rf_model or not self.if_model:
            return None

        processed_data = self._preprocess(feature_vector)

        # 1. Random Forest (Supervised) Prediction
        # Predicts a specific class (e.g., 0 for benign, 1 for anomaly).
        rf_prediction = self.rf_model.predict(processed_data)[0]
        # Predicts the probability of each class. We are interested in the probability of class '1' (anomaly).
        rf_proba = self.rf_model.predict_proba(processed_data)[0]

        # 2. Isolation Forest (Unsupervised) Prediction
        # decision_function returns the anomaly score. Lower scores are more anomalous.
        if_score = self.if_model.decision_function(processed_data)[0]
        # predict returns -1 for anomalies (outliers) and 1 for inliers.
        if_prediction = self.if_model.predict(processed_data)[0]

        return {
            'rf_prediction': int(rf_prediction),
            'rf_probability': float(rf_proba[1]) if len(rf_proba) > 1 else float(rf_proba[0]),
            'if_score': float(if_score),
            'if_prediction': int(if_prediction),
            'is_anomaly': bool(rf_prediction == 1 or if_prediction == -1)
        }
