import os
import json
import time
import logging
import requests
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union

# Local imports
from models.isolation_forest import IsolationForestModel
from models.random_forest import RandomForestModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("inference.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("inference")

class InferenceEngine:
    """
    Real-time inference engine for network intrusion detection.
    
    This class loads trained models and performs inference on incoming network flow features
    to detect anomalies and classify attack types.
    """
    
    def __init__(
        self,
        isolation_forest_path: str = "models/isolation_forest_model.joblib",
        random_forest_path: str = "models/random_forest_model.joblib",
        feature_config_path: str = "config/feature_config.json",
        alert_threshold: float = 0.9,
        batch_size: int = 100
    ):
        """
        Initialize the inference engine with pre-trained models.
        
        Args:
            isolation_forest_path: Path to the trained isolation forest model
            random_forest_path: Path to the trained random forest classifier
            feature_config_path: Path to feature configuration (scaling, encoding, etc.)
            alert_threshold: Threshold for classification confidence to generate alerts
            batch_size: Number of flows to process in a batch
        """
        self.isolation_forest_path = isolation_forest_path
        self.random_forest_path = random_forest_path
        self.feature_config_path = feature_config_path
        self.alert_threshold = alert_threshold
        self.batch_size = batch_size
        
        # Load models
        self.isolation_forest = self._load_isolation_forest()
        self.random_forest = self._load_random_forest()
        self.feature_config = self._load_feature_config()
        
        # API endpoints
        self.api_gateway_url = os.getenv("API_GATEWAY_URL", "http://localhost:5001")
        self.supabase_url = os.getenv("SUPABASE_URL", "")
        self.supabase_key = os.getenv("SUPABASE_KEY", "")
        
        # Statistics
        self.stats = {
            "flows_processed": 0,
            "anomalies_detected": 0,
            "alerts_generated": 0,
            "processing_time": 0,
            "start_time": time.time(),
            "last_processed_time": None
        }
        
        logger.info("Inference engine initialized")
    
    def _load_isolation_forest(self) -> IsolationForestModel:
        """Load the isolation forest model for anomaly detection."""
        try:
            model = IsolationForestModel.load_model(self.isolation_forest_path)
            logger.info(f"Isolation Forest model loaded from {self.isolation_forest_path}")
            return model
        except Exception as e:
            logger.error(f"Error loading Isolation Forest model: {str(e)}")
            # Create a default model with conservative parameters
            logger.warning("Creating a default Isolation Forest model")
            model = IsolationForestModel(contamination=0.01)
            return model
    
    def _load_random_forest(self) -> RandomForestModel:
        """Load the random forest model for attack classification."""
        try:
            model = RandomForestModel()
            model.load_model(self.random_forest_path)
            logger.info(f"Random Forest model loaded from {self.random_forest_path}")
            return model
        except Exception as e:
            logger.error(f"Error loading Random Forest model: {str(e)}")
            # Create a default model with conservative parameters
            logger.warning("Creating a default Random Forest model")
            model = RandomForestModel(n_estimators=100)
            return model
    
    def _load_feature_config(self) -> Dict:
        """Load feature configuration for preprocessing."""
        try:
            with open(self.feature_config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Feature configuration loaded from {self.feature_config_path}")
            return config
        except Exception as e:
            logger.error(f"Error loading feature configuration: {str(e)}")
            # Return default configuration
            return {
                "required_features": [],
                "categorical_features": [],
                "numerical_features": [],
                "scaling": "standard"
            }
    
    def preprocess_features(self, flow_data: Dict) -> Optional[pd.DataFrame]:
        """
        Preprocess flow data for model inference.
        
        Args:
            flow_data: Dictionary containing flow features
            
        Returns:
            DataFrame of preprocessed features ready for model input
        """
        try:
            # Extract features dictionary
            features = flow_data.get("features", {})
            if not features:
                logger.warning("No features found in flow data")
                return None
            
            # Create DataFrame
            df = pd.DataFrame([features])
            
            # Check for required features
            required = self.feature_config.get("required_features", [])
            if required and not all(feat in df.columns for feat in required):
                missing = [feat for feat in required if feat not in df.columns]
                logger.warning(f"Missing required features: {missing}")
                
                # Fill missing features with defaults (0)
                for feat in missing:
                    df[feat] = 0
            
            # Apply preprocessing based on feature config
            # This would include scaling, one-hot encoding, etc.
            # Simplified version here
            
            return df
            
        except Exception as e:
            logger.error(f"Error preprocessing features: {str(e)}")
            return None
    
    def detect_anomalies(self, features: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect anomalies using the isolation forest model.
        
        Args:
            features: DataFrame of preprocessed features
            
        Returns:
            Tuple of (predictions, scores) where:
                - predictions: -1 for anomaly, 1 for normal
                - scores: Anomaly scores (higher = more anomalous)
        """
        try:
            # Get raw predictions (-1 for anomaly, 1 for normal)
            predictions = self.isolation_forest.predict(features)
            
            # Get decision function scores (negative = more anomalous)
            scores = self.isolation_forest.decision_function(features)
            
            # Convert scores to anomaly probability (higher = more anomalous)
            scores = 0.5 - scores/2  # Transform to 0-1 range where higher is more anomalous
            
            return predictions, scores
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            # Return safe defaults (all normal)
            return np.ones(len(features)), np.zeros(len(features))
    
    def classify_attacks(self, features: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Classify attack types using the random forest model.
        
        Args:
            features: DataFrame of preprocessed features
            
        Returns:
            Tuple of (predictions, probabilities) where:
                - predictions: Predicted attack class labels
                - probabilities: Class probabilities for each sample
        """
        try:
            # Get predictions
            predictions = self.random_forest.predict(features)
            
            # Get prediction probabilities
            probabilities = self.random_forest.predict_proba(features)
            
            return predictions, probabilities
            
        except Exception as e:
            logger.error(f"Error classifying attacks: {str(e)}")
            # Return safe defaults
            return np.array(["normal"] * len(features)), np.array([[1.0, 0.0, 0.0]] * len(features))
    
    def process_flow(self, flow_data: Dict) -> Dict:
        """
        Process a single flow, detect anomalies and generate alerts if necessary.
        
        Args:
            flow_data: Dictionary containing flow information and features
            
        Returns:
            Dictionary with analysis results
        """
        start_time = time.time()
        
        # Preprocess features
        features_df = self.preprocess_features(flow_data)
        if features_df is None:
            return {"error": "Could not preprocess features"}
        
        # Detect anomalies
        anomaly_preds, anomaly_scores = self.detect_anomalies(features_df)
        
        # Classify attacks only if anomaly detected
        attack_types = []
        attack_probs = []
        max_probs = []
        
        for i, is_anomaly in enumerate(anomaly_preds):
            if is_anomaly == -1:  # Anomaly detected
                # Run classification
                pred_types, pred_probs = self.classify_attacks(features_df.iloc[[i]])
                attack_type = pred_types[0]
                max_prob = np.max(pred_probs[0])
                
                attack_types.append(attack_type)
                max_probs.append(max_prob)
            else:
                attack_types.append("normal")
                max_probs.append(0.0)
        
        # Determine if we should generate an alert
        should_alert = False
        alert_reasons = []
        
        for i, (is_anomaly, attack_type, max_prob) in enumerate(zip(anomaly_preds, attack_types, max_probs)):
            if is_anomaly == -1 and attack_type != "normal" and max_prob >= self.alert_threshold:
                should_alert = True
                alert_reasons.append(f"{attack_type} (confidence: {max_prob:.2f})")
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Update stats
        self.stats["flows_processed"] += 1
        self.stats["processing_time"] += processing_time
        self.stats["last_processed_time"] = time.time()
        
        if should_alert:
            self.stats["anomalies_detected"] += 1
            
            # Generate alert
            self._generate_alert(flow_data, attack_types[0], max_probs[0], anomaly_scores[0])
            self.stats["alerts_generated"] += 1
        
        # Create result dictionary
        result = {
            "flow_id": flow_data.get("flow_id", "unknown"),
            "is_anomaly": bool(anomaly_preds[0] == -1),
            "anomaly_score": float(anomaly_scores[0]),
            "attack_type": attack_types[0],
            "attack_probability": float(max_probs[0]),
            "processing_time": processing_time,
            "should_alert": should_alert,
            "alert_reasons": alert_reasons
        }
        
        return result
    
    def _generate_alert(self, flow_data: Dict, attack_type: str, confidence: float, anomaly_score: float) -> None:
        """
        Generate an alert and send it to the API Gateway.
        
        Args:
            flow_data: Dictionary containing flow information
            attack_type: Detected attack type
            confidence: Model confidence in the attack classification
            anomaly_score: Anomaly score from isolation forest
        """
        try:
            # Determine severity based on confidence and anomaly score
            severity = "low"
            if confidence >= 0.8 or anomaly_score >= 0.8:
                severity = "high"
            elif confidence >= 0.6 or anomaly_score >= 0.6:
                severity = "medium"
            
            # Create alert message
            message = f"Detected {attack_type} attack from {flow_data.get('src_ip')}:{flow_data.get('src_port')} to {flow_data.get('dst_ip')}:{flow_data.get('dst_port')}"
            
            # Create alert payload
            alert = {
                "severity": severity,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "source": flow_data.get("src_ip", "unknown"),
                "flow_id": flow_data.get("flow_id", "unknown"),
                "metadata": {
                    "attack_type": attack_type,
                    "confidence": confidence,
                    "anomaly_score": anomaly_score,
                    "protocol": flow_data.get("protocol", "unknown"),
                    "src_port": flow_data.get("src_port", 0),
                    "dst_port": flow_data.get("dst_port", 0)
                }
            }
            
            # Send alert to API Gateway
            if self.api_gateway_url:
                try:
                    response = requests.post(
                        f"{self.api_gateway_url}/api/alerts",
                        json=alert,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code != 201:
                        logger.warning(f"Failed to send alert to API Gateway: {response.status_code} {response.text}")
                except Exception as e:
                    logger.error(f"Error sending alert to API Gateway: {str(e)}")
            
            logger.info(f"Alert generated: {message} (Severity: {severity})")
            
        except Exception as e:
            logger.error(f"Error generating alert: {str(e)}")
    
    def get_stats(self) -> Dict:
        """Get current statistics."""
        # Calculate derived stats
        uptime = time.time() - self.stats["start_time"]
        flows_per_sec = self.stats["flows_processed"] / max(1, uptime)
        avg_processing_time = self.stats["processing_time"] / max(1, self.stats["flows_processed"])
        
        return {
            **self.stats,
            "uptime": uptime,
            "flows_per_sec": flows_per_sec,
            "avg_processing_time": avg_processing_time,
            "anomaly_rate": self.stats["anomalies_detected"] / max(1, self.stats["flows_processed"])
        }


def main():
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='NIDS ML Inference Engine')
    parser.add_argument('--isolation-forest', help='Path to isolation forest model')
    parser.add_argument('--random-forest', help='Path to random forest model')
    parser.add_argument('--feature-config', help='Path to feature configuration')
    parser.add_argument('--alert-threshold', type=float, help='Alert threshold', default=0.9)
    parser.add_argument('--batch-size', type=int, help='Batch size', default=100)
    args = parser.parse_args()
    
    # Create inference engine
    engine = InferenceEngine(
        isolation_forest_path=args.isolation_forest or "models/isolation_forest_model.joblib",
        random_forest_path=args.random_forest or "models/random_forest_model.joblib",
        feature_config_path=args.feature_config or "config/feature_config.json",
        alert_threshold=args.alert_threshold,
        batch_size=args.batch_size
    )
    
    # Start processing flows
    logger.info("Inference engine started - waiting for flow data")
    
    # In a real implementation, this would likely be:
    # 1. A REST API endpoint receiving flow data
    # 2. A Kafka consumer reading from a flow topic
    # 3. A direct database subscription to flow records
    
    # For demonstration, we'll simulate some flows
    from time import sleep
    
    try:
        while True:
            # In production, this would be replaced with actual flow data from your data source
            
            # Print stats every 10 seconds
            stats = engine.get_stats()
            logger.info(f"Stats: {stats['flows_processed']} flows processed, "
                       f"{stats['anomalies_detected']} anomalies detected, "
                       f"{stats['alerts_generated']} alerts generated, "
                       f"{stats['avg_processing_time']:.4f}s avg processing time")
            
            sleep(10)
            
    except KeyboardInterrupt:
        logger.info("Inference engine stopped by user")


if __name__ == "__main__":
    main()