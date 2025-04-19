from sklearn.ensemble import IsolationForest, RandomForestClassifier
import joblib
import pandas as pd
import numpy as np
import json
import os
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union, Any
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, confusion_matrix, 
    precision_recall_curve, roc_curve, auc,
    accuracy_score, precision_score, recall_score, f1_score
)

from models.isolation_forest import IsolationForestModel
from models.random_forest import RandomForestModel
from utils import calculate_metrics, save_model, load_model

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("training.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("training")

class ModelTrainer:
    """
    Handles training and retraining of machine learning models for network intrusion detection.
    
    This class is responsible for:
    1. Loading and preprocessing training data
    2. Training anomaly detection models (Isolation Forest)
    3. Training classification models (Random Forest)
    4. Evaluating model performance
    5. Saving trained models
    """
    
    def __init__(
        self,
        data_dir: str = "data",
        models_dir: str = "models",
        config_dir: str = "config",
        results_dir: str = "results"
    ):
        """
        Initialize the model trainer.
        
        Args:
            data_dir: Directory containing training data
            models_dir: Directory to save trained models
            config_dir: Directory containing configuration files
            results_dir: Directory to save training results
        """
        self.data_dir = data_dir
        self.models_dir = models_dir
        self.config_dir = config_dir
        self.results_dir = results_dir
        
        # Create directories if they don't exist
        for directory in [self.data_dir, self.models_dir, self.config_dir, self.results_dir]:
            os.makedirs(directory, exist_ok=True)
            
        # Load configuration
        self.config = self._load_config()
        
        # Initialize metrics
        self.metrics = {
            "isolation_forest": {},
            "random_forest": {}
        }
        
        logger.info("ModelTrainer initialized")
    
    def _load_config(self) -> Dict:
        """
        Load training configuration.
        
        Returns:
            Dictionary containing configuration parameters
        """
        config_path = os.path.join(self.config_dir, "training_config.json")
        
        # Default configuration
        default_config = {
            "isolation_forest": {
                "contamination": 0.01,
                "n_estimators": 100,
                "max_samples": "auto",
                "random_state": 42
            },
            "random_forest": {
                "n_estimators": 100,
                "max_depth": 10,
                "min_samples_split": 2,
                "random_state": 42
            },
            "training": {
                "test_size": 0.2,
                "validation_size": 0.1,
                "retrain_interval_hours": 24,
                "min_samples_for_training": 1000,
                "class_weight": "balanced",
                "feature_selection_method": "importance",
                "top_features": 20
            },
            "feature_extraction": {
                "categorical_features": [],
                "numerical_features": [],
                "feature_scaling": "standard"
            }
        }
        
        # Load configuration if it exists
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                logger.info(f"Configuration loaded from {config_path}")
                
                # Merge with default config to ensure all keys are present
                for section, section_config in default_config.items():
                    if section not in config:
                        config[section] = section_config
                    else:
                        for key, value in section_config.items():
                            if key not in config[section]:
                                config[section][key] = value
                
                return config
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
        
        # Return default if loading failed
        logger.warning("Using default configuration")
        return default_config
    
    def load_data(self, filename: str = None) -> pd.DataFrame:
        """
        Load training data from file.
        
        Args:
            filename: Name of the file to load (if None, load latest)
            
        Returns:
            DataFrame containing training data
        """
        if filename is None:
            # Find latest data file
            data_files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv') or f.endswith('.parquet')]
            if not data_files:
                raise FileNotFoundError(f"No data files found in {self.data_dir}")
            
            # Sort by modified time (newest first)
            data_files.sort(key=lambda f: os.path.getmtime(os.path.join(self.data_dir, f)), reverse=True)
            filename = data_files[0]
        
        file_path = os.path.join(self.data_dir, filename)
        logger.info(f"Loading data from {file_path}")
        
        # Load data based on file extension
        if filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif filename.endswith('.parquet'):
            df = pd.read_parquet(file_path)
        else:
            raise ValueError(f"Unsupported file format: {filename}")
        
        logger.info(f"Loaded {len(df)} samples with {len(df.columns)} features")
        return df
    
    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess data for training.
        
        Args:
            data: Raw data DataFrame
            
        Returns:
            Preprocessed DataFrame
        """
        logger.info("Preprocessing data")
        
        # Make a copy to avoid modifying the original
        df = data.copy()
        
        # Handle missing values
        df = df.fillna(0)
        
        # Remove constant features
        const_features = [col for col in df.columns if df[col].nunique() == 1]
        if const_features:
            logger.info(f"Removing {len(const_features)} constant features")
            df = df.drop(columns=const_features)
        
        # Log data shape
        logger.info(f"Data shape after preprocessing: {df.shape}")
        
        return df
    
    def _split_features_target(
        self, 
        data: pd.DataFrame, 
        target_column: str = 'label'
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Split features and target from data.
        
        Args:
            data: DataFrame containing features and target
            target_column: Name of the target column
            
        Returns:
            Tuple of (features_df, target_series)
        """
        if target_column not in data.columns:
            raise ValueError(f"Target column '{target_column}' not found in data")
        
        X = data.drop(columns=[target_column])
        y = data[target_column]
        
        return X, y
    
    def train_isolation_forest(
        self, 
        data: pd.DataFrame,
        save_model_path: str = None
    ) -> Tuple[IsolationForestModel, Dict]:
        """
        Train an Isolation Forest model for anomaly detection.
        
        Args:
            data: DataFrame containing features (unlabeled)
            save_model_path: Path to save the trained model (if None, use default)
            
        Returns:
            Tuple of (trained_model, performance_metrics)
        """
        logger.info("Training Isolation Forest model")
        start_time = time.time()
        
        # Get parameters from config
        params = self.config["isolation_forest"]
        
        # Initialize model
        model = IsolationForestModel(
            contamination=params["contamination"],
            random_state=params["random_state"]
        )
        
        # Train model
        model.fit(data)
        
        # Get model predictions (-1 for anomaly, 1 for normal)
        predictions = model.predict(data)
        anomaly_count = (predictions == -1).sum()
        
        # Calculate training metrics
        metrics = {
            "training_time": time.time() - start_time,
            "n_samples": len(data),
            "n_features": data.shape[1],
            "anomaly_rate": anomaly_count / len(data),
            "n_anomalies": int(anomaly_count),
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Save metrics
        self.metrics["isolation_forest"] = metrics
        
        # Save model if path provided
        if save_model_path is None:
            save_model_path = os.path.join(
                self.models_dir, 
                f"isolation_forest_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.joblib"
            )
        
        model.save_model(save_model_path)
        logger.info(f"Isolation Forest model trained and saved to {save_model_path}")
        logger.info(f"Anomaly rate: {metrics['anomaly_rate']:.4f} ({metrics['n_anomalies']} anomalies detected)")
        
        return model, metrics
    
    def train_random_forest(
        self, 
        data: pd.DataFrame,
        target_column: str = 'label', 
        save_model_path: str = None
    ) -> Tuple[RandomForestModel, Dict]:
        """
        Train a Random Forest model for attack classification.
        
        Args:
            data: DataFrame containing features and target
            target_column: Name of the target column
            save_model_path: Path to save the trained model (if None, use default)
            
        Returns:
            Tuple of (trained_model, performance_metrics)
        """
        logger.info("Training Random Forest model")
        start_time = time.time()
        
        # Split features and target
        X, y = self._split_features_target(data, target_column)
        
        # Split into training and test sets
        test_size = self.config["training"]["test_size"]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.config["random_forest"]["random_state"]
        )
        
        # Get parameters from config
        params = self.config["random_forest"]
        
        # Initialize model
        model = RandomForestModel(
            n_estimators=params["n_estimators"],
            random_state=params["random_state"]
        )
        
        # Train model
        model.train(X_train, y_train)
        
        # Evaluate model
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        metrics = {
            "training_time": time.time() - start_time,
            "n_samples": len(X),
            "n_features": X.shape[1],
            "test_size": test_size,
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, average='weighted'),
            "recall": recall_score(y_test, y_pred, average='weighted'),
            "f1": f1_score(y_test, y_pred, average='weighted'),
            "class_distribution": dict(y.value_counts().to_dict()),
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Get class-specific metrics
        class_report = classification_report(y_test, y_pred, output_dict=True)
        metrics["class_report"] = class_report
        
        # Feature importance
        feature_importance = model.model.feature_importances_
        metrics["feature_importance"] = dict(zip(X.columns, feature_importance))
        
        # Save metrics
        self.metrics["random_forest"] = metrics
        
        # Generate confusion matrix and save as image
        self._save_confusion_matrix(y_test, y_pred)
        
        # Save model if path provided
        if save_model_path is None:
            save_model_path = os.path.join(
                self.models_dir, 
                f"random_forest_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.joblib"
            )
        
        model.save_model(save_model_path)
        logger.info(f"Random Forest model trained and saved to {save_model_path}")
        logger.info(f"Accuracy: {metrics['accuracy']:.4f}, F1: {metrics['f1']:.4f}")
        
        return model, metrics
    
    def _save_confusion_matrix(self, y_true: np.ndarray, y_pred: np.ndarray) -> None:
        """
        Generate and save confusion matrix visualization.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
        """
        try:
            plt.figure(figsize=(10, 8))
            cm = confusion_matrix(y_true, y_pred)
            sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", 
                        xticklabels=sorted(set(y_true)),
                        yticklabels=sorted(set(y_true)))
            plt.xlabel('Predicted')
            plt.ylabel('True')
            plt.title('Confusion Matrix')
            
            # Save figure
            cm_path = os.path.join(
                self.results_dir, 
                f"confusion_matrix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            plt.savefig(cm_path)
            plt.close()
            logger.info(f"Confusion matrix saved to {cm_path}")
        except Exception as e:
            logger.error(f"Error saving confusion matrix: {str(e)}")
    
    def save_metrics(self) -> None:
        """Save training metrics to file."""
        metrics_path = os.path.join(
            self.results_dir, 
            f"training_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        try:
            with open(metrics_path, 'w') as f:
                json.dump(self.metrics, f, indent=2)
            logger.info(f"Training metrics saved to {metrics_path}")
        except Exception as e:
            logger.error(f"Error saving metrics: {str(e)}")
    
    def save_feature_config(self, features_df: pd.DataFrame) -> None:
        """
        Save feature configuration for inference preprocessing.
        
        Args:
            features_df: DataFrame containing features
        """
        feature_config = {
            "required_features": features_df.columns.tolist(),
            "categorical_features": self.config["feature_extraction"]["categorical_features"],
            "numerical_features": self.config["feature_extraction"]["numerical_features"],
            "scaling": self.config["feature_extraction"]["feature_scaling"]
        }
        
        config_path = os.path.join(self.config_dir, "feature_config.json")
        
        try:
            with open(config_path, 'w') as f:
                json.dump(feature_config, f, indent=2)
            logger.info(f"Feature configuration saved to {config_path}")
        except Exception as e:
            logger.error(f"Error saving feature configuration: {str(e)}")
    
    def run_training_pipeline(
        self, 
        data_path: str = None,
        target_column: str = 'label',
        save_models: bool = True
    ) -> Dict:
        """
        Run the complete training pipeline.
        
        Args:
            data_path: Path to the training data file (if None, use latest)
            target_column: Name of the target column for supervised training
            save_models: Whether to save trained models
            
        Returns:
            Dictionary containing training metrics
        """
        logger.info("Starting training pipeline")
        
        # Load data
        try:
            data = self.load_data(data_path)
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return {"error": str(e)}
        
        # Preprocess data
        try:
            data = self.preprocess_data(data)
        except Exception as e:
            logger.error(f"Error preprocessing data: {str(e)}")
            return {"error": str(e)}
        
        # Save feature configuration for inference
        self.save_feature_config(data.drop(columns=[target_column]) if target_column in data.columns else data)
        
        # Train unsupervised model (Isolation Forest)
        try:
            # For unsupervised training, use all features but exclude the target
            unsupervised_data = data.drop(columns=[target_column]) if target_column in data.columns else data
            
            # Model paths
            if save_models:
                iso_model_path = os.path.join(self.models_dir, "isolation_forest_model.joblib")
            else:
                iso_model_path = None
                
            _, iso_metrics = self.train_isolation_forest(unsupervised_data, iso_model_path)
        except Exception as e:
            logger.error(f"Error training Isolation Forest: {str(e)}")
            iso_metrics = {"error": str(e)}
        
        # Train supervised model (Random Forest) only if target column exists
        rf_metrics = {}
        if target_column in data.columns:
            try:
                # Model paths
                if save_models:
                    rf_model_path = os.path.join(self.models_dir, "random_forest_model.joblib")
                else:
                    rf_model_path = None
                    
                _, rf_metrics = self.train_random_forest(data, target_column, rf_model_path)
            except Exception as e:
                logger.error(f"Error training Random Forest: {str(e)}")
                rf_metrics = {"error": str(e)}
        else:
            logger.warning(f"Target column '{target_column}' not found in data. Skipping supervised training.")
        
        # Save metrics
        self.save_metrics()
        
        # Return combined metrics
        return {
            "isolation_forest": iso_metrics,
            "random_forest": rf_metrics,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


def main():
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='NIDS ML Model Trainer')
    parser.add_argument('--data', help='Path to training data file')
    parser.add_argument('--target', default='label', help='Name of target column')
    parser.add_argument('--no-save', action='store_true', help='Do not save models')
    args = parser.parse_args()
    
    # Create trainer
    trainer = ModelTrainer()
    
    # Run training pipeline
    metrics = trainer.run_training_pipeline(
        data_path=args.data,
        target_column=args.target,
        save_models=not args.no_save
    )
    
    # Print summary
    print("\n--- Training Results ---")
    if "isolation_forest" in metrics and "error" not in metrics["isolation_forest"]:
        print("\nIsolation Forest:")
        print(f"  Anomaly Rate: {metrics['isolation_forest']['anomaly_rate']:.4f}")
        print(f"  Anomalies Detected: {metrics['isolation_forest']['n_anomalies']}")
        print(f"  Training Time: {metrics['isolation_forest']['training_time']:.2f}s")
    
    if "random_forest" in metrics and "error" not in metrics["random_forest"]:
        print("\nRandom Forest:")
        print(f"  Accuracy: {metrics['random_forest']['accuracy']:.4f}")
        print(f"  F1 Score: {metrics['random_forest']['f1']:.4f}")
        print(f"  Precision: {metrics['random_forest']['precision']:.4f}")
        print(f"  Recall: {metrics['random_forest']['recall']:.4f}")
        print(f"  Training Time: {metrics['random_forest']['training_time']:.2f}s")
    
    print("\n--- Training completed successfully ---\n")


if __name__ == "__main__":
    main()