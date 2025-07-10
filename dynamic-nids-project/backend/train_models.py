# backend/train_models.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

def train_and_evaluate_models():
    """
    This function loads a dataset, trains the Random Forest and Isolation Forest
    models, evaluates their performance, and saves them to disk for later use.
    """
    # --- 1. Data Loading and Preparation ---
    print("Loading and preparing dataset...")
    
    # In a real-world scenario, you would load a comprehensive, labeled dataset.
    # Example: data_path = 'datasets/cicids2017_traffic.csv'
    # For this prototype, we will use a small, synthetic dataset.
    # The 'label' column is crucial for supervised training: 0=benign, 1=malicious.
    synthetic_data = {
        'packet_length': [64, 1500, 128, 1024, 60, 32, 1400, 256, 512, 2048],
        'tcp_flags': [2, 24, 18, 24, 2, 2, 49, 24, 18, 4], # SYN, ACK, SYN-ACK, ACK, SYN, SYN, URG-ACK, ACK, SYN-ACK, RST
        'src_port': [12345, 80, 443, 22, 1234, 9999, 53, 25, 110, 135],
        'dst_port': [80, 12345, 12346, 12347, 443, 1337, 12348, 12349, 12350, 12351],
        'label': [0, 0, 0, 0, 0, 1, 1, 0, 0, 1] # 1 indicates an anomaly/attack
    }
    data = pd.DataFrame(synthetic_data)
    
    # Define features (X) and the target variable (y)
    features = ['packet_length', 'tcp_flags', 'src_port', 'dst_port']
    target = 'label'
    X = data[features]
    y = data[target]

    # --- 2. Train Random Forest Classifier (Supervised) ---
    print("\n--- Training Random Forest Classifier ---")
    # Split data into training and testing sets for evaluation
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    
    # Initialize and train the classifier
    rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42, oob_score=True, class_weight='balanced')
    rf_classifier.fit(X_train, y_train)
    
    # Evaluate the model
    print("Evaluating Random Forest model...")
    y_pred_rf = rf_classifier.predict(X_test)
    print("Classification Report:")
    print(classification_report(y_test, y_pred_rf))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred_rf))
    print(f"Out-of-Bag (OOB) Score: {rf_classifier.oob_score_:.4f}")

    # --- 3. Train Isolation Forest (Unsupervised) ---
    print("\n--- Training Isolation Forest ---")
    # For unsupervised anomaly detection, it's best to train on normal data.
    X_normal = X[y == 0]
    
    # The 'contamination' parameter estimates the proportion of outliers in the data.
    # 'auto' is a good starting point, but can be tuned.
    iso_forest = IsolationForest(n_estimators=100, contamination='auto', random_state=42)
    iso_forest.fit(X_normal)
    
    # Evaluate Isolation Forest on the full test set
    y_pred_if = iso_forest.predict(X_test)
    # Convert predictions: 1 (inlier) -> 0 (benign), -1 (outlier) -> 1 (malicious)
    y_pred_if_mapped = [0 if x == 1 else 1 for x in y_pred_if]
    print("Evaluating Isolation Forest model (on test set):")
    print(classification_report(y_test, y_pred_if_mapped))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred_if_mapped))

    # --- 4. Save Models to Disk ---
    print("\nSaving trained models...")
    models_dir = 'models'
    os.makedirs(models_dir, exist_ok=True)
    
    rf_model_path = os.path.join(models_dir, 'rf_model.joblib')
    joblib.dump(rf_classifier, rf_model_path)
    print(f"Random Forest model saved to '{rf_model_path}'")
    
    if_model_path = os.path.join(models_dir, 'if_model.joblib')
    joblib.dump(iso_forest, if_model_path)
    print(f"Isolation Forest model saved to '{if_model_path}'")

if __name__ == "__main__":
    train_and_evaluate_models()
