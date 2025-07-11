# backend/quick_test.py

"""
Quick test of robust ML services
"""

import warnings
warnings.filterwarnings('ignore')

import os
os.environ['PYTHONWARNINGS'] = 'ignore'

try:
    print("Testing robust ML services...")
    from ml_services_robust import get_robust_ml_services
    
    # Initialize services
    ml_services = get_robust_ml_services()
    print(f"ML services initialized: {type(ml_services).__name__}")
    
    # Test prediction
    test_features = {
        'packet_length': 1500,
        'tcp_flags': 24,
        'src_port': 80,
        'dst_port': 1234,
        'src_addr': '192.168.1.1',
        'dst_addr': '192.168.1.2'
    }
    
    import asyncio
    
    async def test_prediction():
        result = await ml_services.predict_anomaly(test_features)
        print("Prediction result:", result)
        return result
    
    # Run test
    result = asyncio.run(test_prediction())
    
    # Get model info
    info = ml_services.get_model_info()
    print("Model info:", info)
    
    print("✅ Robust ML services test completed successfully!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
