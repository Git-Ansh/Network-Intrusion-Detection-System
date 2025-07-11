# backend/test_ml_quick.py

"""
Quick test of ML services without hanging imports
"""

import warnings
warnings.filterwarnings('ignore')

import os
os.environ['PYTHONWARNINGS'] = 'ignore'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'

print("Testing ML Services...")

try:
    print("1. Testing ML libraries...")
    
    # Test pandas import
    try:
        import pandas as pd
        print("   ✓ pandas imported")
    except ImportError as e:
        print(f"   ✗ pandas failed: {e}")
    
    # Test numpy import 
    try:
        import numpy as np
        print("   ✓ numpy imported")
    except ImportError as e:
        print(f"   ✗ numpy failed: {e}")
        
    # Test sklearn import
    try:
        from sklearn.ensemble import RandomForestClassifier
        print("   ✓ scikit-learn imported")
    except ImportError as e:
        print(f"   ✗ scikit-learn failed: {e}")
    
    print("2. Testing ML services module...")
    from ml_services import MLServices
    print("   ✓ MLServices imported")
    
    # Create ML services instance
    ml_services = MLServices()
    print(f"   ✓ ML Available: {ml_services.ml_available}")
    
    print("3. Testing anomaly detection...")
    # Test anomaly detection with sample data
    import asyncio
    sample_data = {
        'packet_size': 1500,
        'protocol': 'TCP',
        'port': 80,
        'time_delta': 0.1
    }
    
    # Test async prediction
    async def test_prediction():
        result = await ml_services.predict_anomaly(sample_data)
        return result
    
    result = asyncio.run(test_prediction())
    print(f"   ✓ Anomaly detection result: {result}")
    
    print("\n✅ ML Services test completed successfully!")
    
except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
