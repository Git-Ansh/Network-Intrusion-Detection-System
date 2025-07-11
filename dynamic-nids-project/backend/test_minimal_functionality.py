# backend/test_minimal_functionality.py

"""
Test minimal backend functionality without external dependencies
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append('.')

async def test_ml_services():
    """Test ML services functionality"""
    print("Testing ML Services Functionality...")
    print("=" * 40)
    
    try:
        # Import and initialize ML services
        from ml_services_minimal import get_ml_services, get_model_status
        
        ml_services = get_ml_services()
        print("✓ ML services initialized")
        
        # Get model status
        model_status = get_model_status()
        print(f"✓ Model status: {model_status['service_type']}")
        
        # Test prediction with normal traffic
        print("\n1. Testing normal traffic...")
        normal_data = {
            'packet_size': 500,
            'protocol': 'TCP',
            'port': 80,
            'time_delta': 0.1
        }
        
        prediction = await ml_services.predict_anomaly(normal_data)
        if prediction:
            print(f"   Anomaly detected: {prediction['is_anomaly']}")
            print(f"   Anomaly score: {prediction['anomaly_score']}")
            print(f"   Reasoning: {prediction['reasoning']}")
        else:
            print("   No prediction returned")
        
        # Test prediction with suspicious traffic
        print("\n2. Testing suspicious traffic...")
        suspicious_data = {
            'packet_size': 200,
            'protocol': 'TCP',
            'port': 1337,
            'time_delta': 0.001
        }
        
        prediction = await ml_services.predict_anomaly(suspicious_data)
        if prediction:
            print(f"   Anomaly detected: {prediction['is_anomaly']}")
            print(f"   Anomaly score: {prediction['anomaly_score']}")
            print(f"   Reasoning: {prediction['reasoning']}")
        else:
            print("   No prediction returned")
        
        # Test with large packet
        print("\n3. Testing large packet...")
        large_packet_data = {
            'packet_size': 1500,
            'protocol': 'TCP',
            'port': 443,
            'time_delta': 0.05
        }
        
        prediction = await ml_services.predict_anomaly(large_packet_data)
        if prediction:
            print(f"   Anomaly detected: {prediction['is_anomaly']}")
            print(f"   Anomaly score: {prediction['anomaly_score']}")
            print(f"   Reasoning: {prediction['reasoning']}")
        else:
            print("   No prediction returned")
        
        # Get model info
        print("\n4. Testing model info...")
        model_info = ml_services.get_model_info()
        print(f"   Active model: {model_info['active_model']}")
        print(f"   Predictions made: {model_info['predictions_made']}")
        
        print("\n✅ All ML services tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ ML services test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backend_import():
    """Test backend import"""
    print("\nTesting Backend Import...")
    print("=" * 40)
    
    try:
        import main_ml_minimal
        print("✓ Backend imported successfully")
        
        # Check if FastAPI app is created
        app = main_ml_minimal.app
        print(f"✓ FastAPI app created: {app.title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Backend import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("NIDS Minimal Backend Functionality Test")
    print("=" * 50)
    
    # Test ML services
    ml_test_passed = await test_ml_services()
    
    # Test backend import
    backend_test_passed = test_backend_import()
    
    print("\n" + "=" * 50)
    if ml_test_passed and backend_test_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\nTo start the server:")
        print("   python main_ml_minimal.py")
        print("\nServer will be available at:")
        print("   http://localhost:8000")
        print("   http://localhost:8000/docs")
    else:
        print("❌ Some tests failed.")
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
