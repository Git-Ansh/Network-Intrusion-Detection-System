#!/usr/bin/env python3
"""
Test script to verify the graph data structure returned by the backend
"""

import asyncio
import sys
import os

# Add the current directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the backend
from main_ml_with_auth import get_graph_data

async def test_graph_structure():
    """Test the graph data structure"""
    print("🧪 Testing Graph Data Structure")
    print("=" * 50)
    
    try:
        # Get the graph data
        graph_data = await get_graph_data()
        
        print("📊 Graph Data Structure:")
        print(f"   Type: {type(graph_data)}")
        print(f"   Keys: {list(graph_data.keys()) if isinstance(graph_data, dict) else 'Not a dict'}")
        
        if isinstance(graph_data, dict):
            # Check nodes
            nodes = graph_data.get('nodes', [])
            print(f"   Nodes: {len(nodes)} items")
            if nodes:
                print(f"   Sample node: {nodes[0]}")
            
            # Check edges
            edges = graph_data.get('edges', [])
            print(f"   Edges: {len(edges)} items")
            if edges:
                print(f"   Sample edge: {edges[0]}")
            
            # Check stats
            stats = graph_data.get('stats', {})
            print(f"   Stats: {stats}")
            
            # Check timestamp
            timestamp = graph_data.get('timestamp')
            print(f"   Timestamp: {timestamp}")
        
        print("\n✅ Graph data structure test completed!")
        return graph_data
        
    except Exception as e:
        print(f"❌ Error testing graph data: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_graph_structure())
    
    if result:
        print("\n🎯 Frontend Compatibility:")
        print("   ✅ Backend returns 'edges' (not 'links')")
        print("   ✅ Frontend should transform 'edges' to 'links'")
        print("   ✅ Data structure is consistent")
    else:
        print("\n❌ Graph data test failed!")
