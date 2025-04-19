#!/usr/bin/env python3
"""
Main application for the ML Engine microservice
This service handles real-time inference for intrusion detection and periodic model training
"""

import os
import time
import logging
import argparse
from datetime import datetime

# Import local modules
from models.isolation_forest import IsolationForestModel
from models.random_forest import RandomForestModel
from connectors.supabase_connector import SupabaseConnector
from utils import calculate_metrics, load_model, save_model

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MLEngineApp:
    """Main application class for the ML Engine"""
    
    def __init__(self, mode="inference"):
        """Initialize the ML Engine application"""
        self.mode = mode
        self.supabase = SupabaseConnector()
        self.isolation_forest = None
        self.random_forest = None
        self.models_dir = os.path.join(os.path.dirname(__file__), "..", "models")
        
        # Create models directory if it doesn't exist
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Load models if in inference mode
        if mode == "inference":
            self._load_models()
    
    def _load_models(self):
        """Load the trained models"""
        try:
            # Load isolation forest model
            isolation_forest_path = os.path.join(self.models_dir, "isolation_forest.joblib")
            if os.path.exists(isolation_forest_path):
                self.isolation_forest = IsolationForestModel.load_model(isolation_forest_path)
                logger.info("Isolation Forest model loaded successfully")
            else:
                logger.warning("Isolation Forest model not found, will need training")
                self.isolation_forest = IsolationForestModel()
            
            # Load random forest model
            random_forest_path = os.path.join(self.models_dir, "random_forest.joblib")
            if os.path.exists(random_forest_path):
                self.random_forest = RandomForestModel()
                self.random_forest.load_model(random_forest_path)
                logger.info("Random Forest model loaded successfully")
            else:
                logger.warning("Random Forest model not found, will need training")
                self.random_forest = RandomForestModel()
        
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            # Initialize new models as fallback
            self.isolation_forest = IsolationForestModel()
            self.random_forest = RandomForestModel()
    
    def run_inference_loop(self):
        """Run the inference loop to process network flows and detect intrusions"""
        logger.info("Starting inference loop")
        
        while True:
            try:
                # Get the latest flow data from Supabase
                flows = self.supabase.get_training_data(limit=100)
                
                if not flows:
                    logger.info("No new flows to process, waiting...")
                    time.sleep(10)
                    continue
                
                logger.info(f"Processing {len(flows)} flows for inference")
                
                # Process each flow
                for flow in flows:
                    # Extract features from flow
                    features = self._extract_features_from_flow(flow)
                    
                    if not features:
                        continue
                    
                    # Run anomaly detection with Isolation Forest
                    is_anomaly = False
                    anomaly_score = 0
                    
                    if self.isolation_forest:
                        # Prediction: -1 for anomalies, 1 for normal
                        prediction = self.isolation_forest.predict([features])[0]
                        is_anomaly = prediction == -1
                        
                        # Calculate anomaly score (decision_function returns negative values for anomalies)
                        anomaly_score = abs(self.isolation_forest.model.decision_function([features])[0])
                        anomaly_score = min(1.0, anomaly_score)  # Normalize to 0-1
                    
                    # Run classification with Random Forest if available
                    alert_type = "Anomaly Detection"
                    if self.random_forest and is_anomaly:
                        alert_type = self.random_forest.predict([features])[0]
                    
                    # Generate alert if anomaly detected
                    if is_anomaly and anomaly_score > 0.5:  # Threshold can be adjusted
                        prediction_data = {
                            'flow_id': flow.get('flow_id'),
                            'flow': flow,
                            'is_anomaly': is_anomaly,
                            'anomaly_score': float(anomaly_score),
                            'alert_type': alert_type,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        # Store prediction as alert
                        result = self.supabase.store_prediction(prediction_data)
                        
                        if result.get('success'):
                            logger.info(f"Alert generated: {alert_type} (score: {anomaly_score:.2f})")
                        else:
                            logger.error(f"Failed to store prediction: {result.get('error')}")
                
                # Sleep before next batch
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in inference loop: {str(e)}")
                time.sleep(30)  # Longer sleep on error
    
    def run_training_loop(self):
        """Run the training loop to periodically retrain models"""
        logger.info("Starting training loop")
        
        while True:
            try:
                logger.info("Starting model training cycle")
                
                # Get training data
                training_data = self.supabase.get_training_data(limit=10000)
                
                if len(training_data) < 100:
                    logger.warning("Insufficient data for training, waiting for more data")
                    time.sleep(3600)  # Wait an hour before trying again
                    continue
                
                logger.info(f"Training with {len(training_data)} flow records")
                
                # Prepare features and labels
                features, labels = self._prepare_training_data(training_data)
                
                # Train Isolation Forest
                self.isolation_forest = IsolationForestModel()
                logger.info("Training Isolation Forest model...")
                self.isolation_forest.fit(features)
                
                # Save Isolation Forest model
                isolation_forest_path = os.path.join(self.models_dir, "isolation_forest.joblib")
                self.isolation_forest.save_model(isolation_forest_path)
                logger.info(f"Isolation Forest model saved to {isolation_forest_path}")
                
                # Train Random Forest if we have labels
                if labels and len(labels) > 0:
                    X_train, X_test, y_train, y_test = train_test_split(
                        features, labels, test_size=0.2, random_state=42
                    )
                    
                    logger.info("Training Random Forest model...")
                    self.random_forest = RandomForestModel()
                    self.random_forest.train(X_train, y_train)
                    
                    # Evaluate model
                    predictions = self.random_forest.predict(X_test)
                    metrics = calculate_metrics(predictions, y_test)
                    
                    # Save Random Forest model
                    random_forest_path = os.path.join(self.models_dir, "random_forest.joblib")
                    self.random_forest.save_model(random_forest_path)
                    logger.info(f"Random Forest model saved to {random_forest_path}")
                    
                    # Update model metadata
                    model_info = {
                        'name': 'random_forest',
                        'accuracy': metrics['accuracy'],
                        'precision': metrics['precision'],
                        'recall': metrics['recall'],
                        'f1_score': metrics['f1_score'],
                        'parameters': self.random_forest.model.get_params(),
                    }
                    self.supabase.update_model_metadata(model_info)
                
                # Wait before next training cycle (e.g., 24 hours)
                logger.info("Training completed. Waiting for next training cycle.")
                time.sleep(86400)  # 24 hours
                
            except Exception as e:
                logger.error(f"Error in training loop: {str(e)}")
                time.sleep(3600)  # Wait an hour before trying again
    
    def _extract_features_from_flow(self, flow):
        """Extract features from a flow record"""
        try:
            features = {}
            
            # Extract basic flow features
            features['bytes'] = flow.get('bytes', 0)
            features['packets'] = flow.get('packets', 0)
            
            # Calculate derived features
            duration = (flow.get('end_time', 0) - flow.get('start_time', 0)) / 1000000  # microseconds to seconds
            features['flow_duration'] = max(0.001, duration)  # Avoid division by zero
            
            features['bytes_per_sec'] = features['bytes'] / features['flow_duration']
            features['packets_per_sec'] = features['packets'] / features['flow_duration']
            features['bytes_per_packet'] = features['bytes'] / max(1, features['packets'])
            
            # Extract feature extraction data if available
            feature_extraction = flow.get('feature_extraction', [])
            if feature_extraction and isinstance(feature_extraction, list):
                for feature in feature_extraction:
                    features[feature.get('feature_name')] = feature.get('feature_value')
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features: {str(e)}")
            return None
    
    def _prepare_training_data(self, flow_data):
        """Prepare training data from flow records"""
        features = []
        labels = []
        
        for flow in flow_data:
            flow_features = self._extract_features_from_flow(flow)
            
            if flow_features:
                features.append(flow_features)
                
                # If we have labels, add them (for supervised learning)
                if 'label' in flow:
                    labels.append(flow['label'])
        
        return features, labels if labels else None


def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(description='ML Engine for Network Intrusion Detection')
    parser.add_argument('--mode', type=str, choices=['inference', 'training'], default='inference',
                        help='Operating mode: inference or training')
    args = parser.parse_args()
    
    try:
        app = MLEngineApp(mode=args.mode)
        
        if args.mode == 'inference':
            app.run_inference_loop()
        elif args.mode == 'training':
            app.run_training_loop()
        
    except KeyboardInterrupt:
        logger.info("ML Engine application stopped by user")
    except Exception as e:
        logger.critical(f"Fatal error in ML Engine: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    # Required import for train_test_split
    from sklearn.model_selection import train_test_split
    exit(main())