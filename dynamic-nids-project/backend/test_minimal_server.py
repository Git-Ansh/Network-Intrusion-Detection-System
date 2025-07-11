# backend/test_minimal_server.py

"""
Test the minimal ML backend server
"""

import requests
import json
import time

def test_server():
    base_url = "http://localhost:8000"
    
    print("Testing Minimal NIDS Backend...")
    print("=" * 40)
    
    try:
        # Test root endpoint
        print("1. Testing root endpoint...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("   ✓ Root endpoint working")
            print(f"   Response: {response.json()['message']}")
        else:
            print(f"   ✗ Root endpoint failed: {response.status_code}")
            return
        
        # Test health endpoint
        print("2. Testing health endpoint...")
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            data = response.json()
            print("   ✓ Health endpoint working")
            print(f"   Status: {data['status']}")
        else:
            print(f"   ✗ Health endpoint failed: {response.status_code}")
        
        # Test ML status endpoint
        print("3. Testing ML status endpoint...")
        response = requests.get(f"{base_url}/api/ml/status")
        if response.status_code == 200:
            data = response.json()
            print("   ✓ ML status endpoint working")
            print(f"   Service type: {data['service_type']}")
        else:
            print(f"   ✗ ML status endpoint failed: {response.status_code}")
        
        # Test ML prediction endpoint
        print("4. Testing ML prediction endpoint...")
        test_data = {
            'packet_size': 1500,
            'protocol': 'TCP',
            'port': 1337,
            'time_delta': 0.001
        }
        response = requests.post(f"{base_url}/api/ml/predict", json=test_data)
        if response.status_code == 200:
            data = response.json()
            prediction = data['prediction']
            print("   ✓ ML prediction endpoint working")
            print(f"   Anomaly detected: {prediction['is_anomaly']}")
            print(f"   Anomaly score: {prediction['anomaly_score']}")
            print(f"   Reasoning: {prediction['reasoning']}")
        else:
            print(f"   ✗ ML prediction endpoint failed: {response.status_code}")
        
        # Test ML test endpoint
        print("5. Testing ML test endpoint...")
        response = requests.get(f"{base_url}/api/ml/test")
        if response.status_code == 200:
            data = response.json()
            print("   ✓ ML test endpoint working")
            print(f"   Test cases: {len(data['test_results'])}")
            for result in data['test_results']:
                status = "✓" if result['status'] == 'success' else "✗"
                anomaly = result['prediction']['is_anomaly'] if 'prediction' in result else 'N/A'
                print(f"     {status} {result['test_case']}: anomaly={anomaly}")
        else:
            print(f"   ✗ ML test endpoint failed: {response.status_code}")
        
        print("\n✅ All tests completed!")
        print("🌐 Backend is running at: http://localhost:8000")
        print("📚 API docs available at: http://localhost:8000/docs")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on port 8000.")
        print("Run: python main_ml_minimal.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_server()
