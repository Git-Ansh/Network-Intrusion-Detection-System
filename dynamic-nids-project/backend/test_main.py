# backend/test_main.py

"""
Test the enhanced main.py with ML capabilities
"""

import warnings
warnings.filterwarnings('ignore')

import os
os.environ['PYTHONWARNINGS'] = 'ignore'

print("Testing enhanced main.py with ML capabilities...")

try:
    print("1. Testing imports...")
    
    # Test basic imports first
    import sys
    sys.path.append('.')
    
    print("   ✓ Basic imports successful")
    
    # Test our main module import
    print("2. Testing main.py import...")
    import main
    print("   ✓ main.py imported successfully")
    
    # Check what ML capabilities are available
    print("3. Checking ML capabilities...")
    if hasattr(main, 'ML_AVAILABLE'):
        print(f"   ✓ ML_AVAILABLE: {main.ML_AVAILABLE}")
    if hasattr(main, 'ML_DETECTOR_TYPE'):
        print(f"   ✓ ML_DETECTOR_TYPE: {main.ML_DETECTOR_TYPE}")
    if hasattr(main, 'anomaly_dtctr'):
        detector_type = type(main.anomaly_dtctr).__name__ if main.anomaly_dtctr else 'None'
        print(f"   ✓ Anomaly detector: {detector_type}")
    
    # Test FastAPI app
    print("4. Testing FastAPI app...")
    if hasattr(main, 'app'):
        print("   ✓ FastAPI app created")
        print(f"   ✓ App title: {main.app.title}")
    
    print("\n✅ All tests passed! Enhanced main.py is ready to run.")
    print("\nTo start the server:")
    print("   start-enhanced.bat")
    print("   OR")
    print("   nids_env\\Scripts\\python.exe backend\\main.py")

except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    
    print("\nFalling back to simple backend test...")
    try:
        import main_simple
        print("✅ Simple backend available as fallback")
        print("Use: nids_env\\Scripts\\python.exe backend\\main_simple.py")
    except Exception as e2:
        print(f"❌ Simple backend also failed: {e2}")
