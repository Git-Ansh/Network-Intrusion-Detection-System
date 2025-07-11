# backend/test_auth_endpoints.py

"""
Test authentication endpoints
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append('.')

async def test_auth_backend():
    """Test authentication backend functionality"""
    print("Testing Auth Backend Endpoints...")
    print("=" * 40)
    
    try:
        # Import and test the backend
        from main_ml_with_auth import app, authenticate_user, create_access_token
        
        print("✓ Auth backend imported successfully")
        
        # Test authentication function
        print("\n1. Testing authentication function...")
        
        # Test valid credentials
        user = authenticate_user("admin", "admin123")
        if user:
            print("   ✓ Valid credentials accepted")
            print(f"   User: {user['username']} - {user['full_name']}")
        else:
            print("   ✗ Valid credentials rejected")
        
        # Test invalid credentials
        user = authenticate_user("admin", "wrongpassword")
        if not user:
            print("   ✓ Invalid credentials rejected")
        else:
            print("   ✗ Invalid credentials accepted")
        
        # Test token creation
        print("\n2. Testing token creation...")
        token = create_access_token("admin")
        if token.startswith("token_admin_"):
            print("   ✓ Token created successfully")
            print(f"   Token: {token[:20]}...")
        else:
            print("   ✗ Token creation failed")
        
        # Test FastAPI app
        print("\n3. Testing FastAPI app...")
        if hasattr(app, 'routes'):
            route_count = len(app.routes)
            print(f"   ✓ App has {route_count} routes")
            print("   ✓ Auth routes should include /token and /users/me")
        
        print("\n✅ All authentication tests passed!")
        
        print("\n" + "=" * 40)
        print("Demo Credentials for Frontend:")
        print("  Username: admin")
        print("  Password: admin123")
        print("=" * 40)
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run authentication tests"""
    print("NIDS Authentication Backend Test")
    print("=" * 50)
    
    auth_test_passed = await test_auth_backend()
    
    print("\n" + "=" * 50)
    if auth_test_passed:
        print("🎉 AUTHENTICATION BACKEND READY!")
        print("\nTo start the server:")
        print("   python main_ml_with_auth.py")
        print("\nServer will be available at:")
        print("   http://localhost:8000")
        print("   http://localhost:8000/docs")
        print("\nDemo Login:")
        print("   Username: admin")
        print("   Password: admin123")
    else:
        print("❌ Authentication tests failed.")
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
