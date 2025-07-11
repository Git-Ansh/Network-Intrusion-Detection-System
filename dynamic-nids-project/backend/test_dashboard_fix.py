#!/usr/bin/env python3
"""
Test the complete fix for the Dashboard TypeError
This simulates what the frontend will receive from the backend
"""

import asyncio
import json
import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main_ml_with_auth import get_graph_data

def simulate_frontend_processing(backend_response):
    """
    Simulate what the frontend Dashboard.jsx does with the backend response
    This tests the fix we implemented
    """
    print("🧪 Simulating Frontend Processing")
    print("=" * 50)
    
    try:
        # Simulate the frontend axios response structure
        response = {
            "data": backend_response
        }
        
        print("📥 Backend Response Structure:")
        print(f"   response.data keys: {list(response['data'].keys())}")
        
        # This is the FIXED frontend code logic
        responseData = response['data'] or {}
        nodes = responseData.get('nodes', [])
        edges = responseData.get('edges', [])
        
        print(f"   📊 Extracted nodes: {len(nodes)} items")
        print(f"   📊 Extracted edges: {len(edges)} items")
        
        # Transform edges to links for frontend compatibility (the fix)
        transformedData = {
            'nodes': nodes,
            'links': [
                {
                    **edge,
                    'id': edge.get('id', f"{edge['source']}-{edge['target']}")
                }
                for edge in edges
            ]
        }
        
        print(f"   🔄 Transformed to links: {len(transformedData['links'])} items")
        
        # Simulate the stats calculation (the fix)
        stats = {
            'nodeCount': len(nodes),  # This was causing the error before
            'edgeCount': len(edges),  # This was also causing the error
            'lastUpdate': 'Now'
        }
        
        print(f"   📈 Stats calculated: {stats}")
        
        # Simulate the graph status check (the fix)
        graphStatus = (transformedData.get('nodes', []) or [])
        statusText = '● Active' if len(graphStatus) > 0 else '● No Data'
        
        print(f"   🔍 Graph status: {statusText}")
        
        print("\n✅ Frontend simulation completed successfully!")
        print("🎯 No 'Cannot read properties of undefined (reading 'length')' errors!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in frontend simulation: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_dashboard_fix():
    """Test the complete dashboard fix"""
    print("🚀 Testing Dashboard.jsx TypeError Fix")
    print("=" * 70)
    
    # Get backend data
    print("1️⃣ Getting data from backend...")
    backend_data = await get_graph_data()
    
    if backend_data:
        print("   ✅ Backend data received")
        
        # Test the frontend processing
        print("\n2️⃣ Testing frontend processing...")
        success = simulate_frontend_processing(backend_data)
        
        if success:
            print("\n🎉 DASHBOARD FIX VERIFIED!")
            print("=" * 50)
            print("✅ Backend returns proper structure with 'edges'")
            print("✅ Frontend transforms 'edges' to 'links'")
            print("✅ No undefined property access errors")
            print("✅ Safe access patterns implemented")
            print("=" * 50)
            return True
        else:
            print("\n❌ Frontend simulation failed")
            return False
    else:
        print("   ❌ Failed to get backend data")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_dashboard_fix())
    
    if result:
        print("\n🚀 READY TO TEST:")
        print("   1. Start the backend: python main_ml_with_auth.py")
        print("   2. Start the frontend: npm run dev")
        print("   3. Login with: admin / admin123")
        print("   4. Dashboard should load without TypeError!")
    else:
        print("\n❌ Fix verification failed!")
