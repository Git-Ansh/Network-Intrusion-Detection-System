# backend/test_ml.py

"""
Test ML dependencies availability and functionality
"""

import sys
import traceback

def test_basic_imports():
    """Test basic Python libraries"""
    try:
        import json
        import asyncio
        import logging
        print("[✓] Basic Python libraries available")
        return True
    except ImportError as e:
        print(f"[✗] Basic libraries failed: {e}")
        return False

def test_fastapi():
    """Test FastAPI and web dependencies"""
    try:
        import fastapi
        import uvicorn
        print(f"[✓] FastAPI available (version: {fastapi.__version__})")
        return True
    except ImportError as e:
        print(f"[✗] FastAPI not available: {e}")
        return False

def test_networking():
    """Test networking libraries"""
    try:
        import pyshark
        import networkx
        import psutil
        print("[✓] Networking libraries available")
        return True
    except ImportError as e:
        print(f"[✗] Networking libraries not available: {e}")
        return False

def test_auth():
    """Test authentication libraries"""
    try:
        from jose import jwt
        from passlib.context import CryptContext
        print("[✓] Authentication libraries available")
        return True
    except ImportError as e:
        print(f"[✗] Authentication libraries not available: {e}")
        return False

def test_ml_basic():
    """Test basic ML libraries"""
    try:
        import numpy as np
        import joblib
        print(f"[✓] Basic ML libraries available (numpy: {np.__version__})")
        return True
    except ImportError as e:
        print(f"[✗] Basic ML libraries not available: {e}")
        return False

def test_ml_advanced():
    """Test advanced ML libraries"""
    results = {}
    
    # Test pandas
    try:
        import pandas as pd
        print(f"[✓] Pandas available (version: {pd.__version__})")
        results['pandas'] = True
    except ImportError as e:
        print(f"[✗] Pandas not available: {e}")
        results['pandas'] = False
    
    # Test scikit-learn
    try:
        import sklearn
        from sklearn.ensemble import RandomForestClassifier, IsolationForest
        print(f"[✓] Scikit-learn available (version: {sklearn.__version__})")
        results['sklearn'] = True
    except ImportError as e:
        print(f"[✗] Scikit-learn not available: {e}")
        results['sklearn'] = False
    
    return results

def test_custom_modules():
    """Test our custom modules"""
    try:
        from simple_detector import SimpleAnomalyDetector
        print("[✓] Simple detector available")
        
        # Test if it works
        detector = SimpleAnomalyDetector()
        print("[✓] Simple detector initialized successfully")
        return True
    except Exception as e:
        print(f"[✗] Simple detector failed: {e}")
        return False

def recommend_startup_mode():
    """Recommend which startup mode to use"""
    print("\n" + "="*50)
    print("RECOMMENDATION")
    print("="*50)
    
    # Test all components
    basic = test_basic_imports()
    fastapi_ok = test_fastapi()
    network_ok = test_networking()
    auth_ok = test_auth()
    ml_basic_ok = test_ml_basic()
    ml_advanced = test_ml_advanced()
    custom_ok = test_custom_modules()
    
    if not basic or not fastapi_ok:
        print("❌ CRITICAL: Basic dependencies missing. System cannot run.")
        return "FAILED"
    
    if not network_ok:
        print("⚠️  WARNING: Network libraries missing. Limited functionality.")
    
    if not auth_ok:
        print("⚠️  WARNING: Auth libraries missing. Use no-auth mode.")
        return "NO_AUTH"
    
    if ml_advanced['pandas'] and ml_advanced['sklearn']:
        print("✅ RECOMMENDATION: Use full ML mode")
        print("   Command: python backend/main_ml.py")
        return "FULL_ML"
    
    elif ml_basic_ok:
        print("✅ RECOMMENDATION: Use basic ML mode")  
        print("   Command: python backend/main.py")
        return "BASIC_ML"
    
    elif custom_ok:
        print("✅ RECOMMENDATION: Use simple mode")
        print("   Command: python backend/main_simple.py")
        return "SIMPLE"
    
    else:
        print("⚠️  RECOMMENDATION: Use minimal mode")
        print("   Command: python backend/main_minimal.py")
        return "MINIMAL"

if __name__ == "__main__":
    print("NIDS ML Dependencies Test")
    print("=" * 50)
    
    try:
        mode = recommend_startup_mode()
        
        print(f"\n🚀 Recommended startup mode: {mode}")
        
        if len(sys.argv) > 1 and sys.argv[1] == "--auto-start":
            if mode == "FULL_ML":
                import subprocess
                print("\n[*] Auto-starting in full ML mode...")
                subprocess.run([sys.executable, "backend/main_ml.py"])
            elif mode == "BASIC_ML":
                import subprocess
                print("\n[*] Auto-starting in basic ML mode...")
                subprocess.run([sys.executable, "backend/main.py"])
            elif mode == "SIMPLE":
                import subprocess
                print("\n[*] Auto-starting in simple mode...")
                subprocess.run([sys.executable, "backend/main_simple.py"])
            elif mode == "MINIMAL":
                import subprocess
                print("\n[*] Auto-starting in minimal mode...")
                subprocess.run([sys.executable, "backend/main_minimal.py"])
                
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        traceback.print_exc()
