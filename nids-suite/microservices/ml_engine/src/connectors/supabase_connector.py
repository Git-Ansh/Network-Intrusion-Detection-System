#!/usr/bin/env python3
"""
Supabase connector for ML Engine
Handles integration between ML predictions and the Supabase database
"""

import os
import json
import logging
from datetime import datetime
from supabase import create_client, Client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SupabaseConnector:
    """
    Connects the ML engine with the Supabase backend to store predictions
    and retrieve training data.
    """
    
    def __init__(self):
        """Initialize the Supabase connector with environment variables"""
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_key = os.environ.get("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            logger.error("Missing Supabase credentials. Set SUPABASE_URL and SUPABASE_KEY environment variables.")
            raise ValueError("Missing Supabase credentials")
        
        self.client = create_client(self.supabase_url, self.supabase_key)
        logger.info("Supabase connector initialized successfully")
    
    def store_prediction(self, prediction):
        """
        Store a prediction in the alerts table
        
        Args:
            prediction (dict): The prediction data from the ML model
        
        Returns:
            dict: The response from Supabase
        """
        try:
            # Format prediction as an alert
            alert = {
                'severity': self._map_severity(prediction.get('anomaly_score', 0)),
                'type': prediction.get('alert_type', 'Anomaly Detection'),
                'description': self._generate_description(prediction),
                'flow_id': prediction.get('flow_id'),
                'created_at': datetime.now().isoformat(),
            }
            
            # Insert into alerts table
            response = self.client.table('alerts').insert(alert).execute()
            
            if hasattr(response, 'error') and response.error:
                logger.error(f"Error storing prediction: {response.error}")
                return {'success': False, 'error': response.error}
            
            logger.info(f"Successfully stored prediction as alert: {alert['type']}")
            return {'success': True, 'data': response.data}
            
        except Exception as e:
            logger.error(f"Error storing prediction: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_training_data(self, limit=1000):
        """
        Retrieve flow data with features for model training
        
        Args:
            limit (int): Maximum number of records to retrieve
        
        Returns:
            list: The flow data with features
        """
        try:
            # Get flows with features
            response = self.client.table('flow_summaries')\
                .select('*, feature_extraction(*)').limit(limit).execute()
            
            if hasattr(response, 'error') and response.error:
                logger.error(f"Error retrieving training data: {response.error}")
                return []
            
            logger.info(f"Successfully retrieved {len(response.data)} flow records for training")
            return response.data
            
        except Exception as e:
            logger.error(f"Error retrieving training data: {str(e)}")
            return []
    
    def update_model_metadata(self, model_info):
        """
        Store model metadata in the database
        
        Args:
            model_info (dict): Information about the trained model
        
        Returns:
            dict: The response from Supabase
        """
        try:
            metadata = {
                'model_name': model_info.get('name'),
                'accuracy': model_info.get('accuracy'),
                'precision': model_info.get('precision'),
                'recall': model_info.get('recall'),
                'f1_score': model_info.get('f1_score'),
                'training_date': datetime.now().isoformat(),
                'parameters': json.dumps(model_info.get('parameters', {})),
            }
            
            # Insert into models table
            response = self.client.table('models').insert(metadata).execute()
            
            if hasattr(response, 'error') and response.error:
                logger.error(f"Error updating model metadata: {response.error}")
                return {'success': False, 'error': response.error}
            
            logger.info(f"Successfully updated model metadata for: {metadata['model_name']}")
            return {'success': True, 'data': response.data}
            
        except Exception as e:
            logger.error(f"Error updating model metadata: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _map_severity(self, anomaly_score):
        """Map anomaly score to severity level"""
        if anomaly_score >= 0.8:
            return 'high'
        elif anomaly_score >= 0.5:
            return 'medium'
        else:
            return 'low'
    
    def _generate_description(self, prediction):
        """Generate a human-readable description for the alert"""
        if 'alert_message' in prediction:
            return prediction['alert_message']
            
        flow = prediction.get('flow', {})
        src_ip = flow.get('src_ip', 'unknown')
        dst_ip = flow.get('dst_ip', 'unknown')
        
        if prediction.get('is_anomaly', False):
            return f"Anomalous network behavior detected between {src_ip} and {dst_ip} (score: {prediction.get('anomaly_score', 0):.2f})"
        else:
            return f"Suspicious traffic pattern between {src_ip} and {dst_ip}"