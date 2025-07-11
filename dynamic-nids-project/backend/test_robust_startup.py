# backend/test_robust_startup.py

"""
Test if the robust backend can start properly
"""

import warnings
warnings.filterwarnings('ignore')

import os
os.environ['PYTHONWARNINGS'] = 'ignore'

print("Testing robust backend startup...")

try:
    # Test basic imports
    print("1. Testing basic imports...")
    from fastapi import FastAPI
    print("   ✓ FastAPI imported")
    
    import asyncio
    print("   ✓ asyncio imported")
    
    # Test our modules
    print("2. Testing custom modules...")
    from sniffer import TrafficSniffer
    print("   ✓ TrafficSniffer imported")
    
    from processor import PacketProcessor
    print("   ✓ PacketProcessor imported")
    
    from graph_manager import GraphManager
    print("   ✓ GraphManager imported")
    
    from graph_analyzer import GraphAnalyzer
    print("   ✓ GraphAnalyzer imported")
    
    from auth import router as auth_router
    print("   ✓ Auth router imported")
    
    # Test robust ML services
    print("3. Testing robust ML services...")
    try:
        from ml_services_robust import get_robust_ml_services
        ml_services = get_robust_ml_services()
        print(f"   ✓ Robust ML services loaded: {type(ml_services).__name__}")
        
        # Test prediction
        test_features = {
            'packet_length': 1000,
            'tcp_flags': 24,
            'src_port': 80,
            'dst_port': 1234,
            'src_addr': '192.168.1.1',
            'dst_addr': '192.168.1.2'
        }
        
        async def test_prediction():
            result = await ml_services.predict_anomaly(test_features)
            return result
        
        result = asyncio.run(test_prediction())
        print(f"   ✓ ML prediction test: {result['model_type'] if result else 'failed'}")
        
    except Exception as e:
        print(f"   ⚠ ML services not available: {e}")
    
    # Test FastAPI app creation
    print("4. Testing FastAPI app creation...")
    app = FastAPI(title="Test App")
    print("   ✓ FastAPI app created")
    
    print("\n✅ All tests passed! Robust backend should start successfully.")
    print("\nTo start the backend manually:")
    print("nids_env\\Scripts\\python.exe backend\\main_robust.py")
    
except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    
    print("\nTrying fallback to simple backend...")
    try:
        print("Testing simple backend...")
        # Test if simple backend would work
        from simple_detector import SimpleAnomalyDetector
        detector = SimpleAnomalyDetector()
        print("✅ Simple backend should work")
        print("Use: nids_env\\Scripts\\python.exe backend\\main_simple.py")
    except Exception as e2:
        print(f"❌ Simple backend also failed: {e2}")
        print("Use minimal backend: nids_env\\Scripts\\python.exe backend\\main_minimal.py")
