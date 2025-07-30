#!/usr/bin/env python
"""
Debug script to test admin panel access
"""

import os
import sys
import django

# Add the current directory to the Python path
sys.path.insert(0, os.getcwd())

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_app.settings')
django.setup()

def test_admin_access():
    print("🔍 Testing Admin Panel Access...")
    
    try:
        from django.test import Client
        from accounts.models import User
        
        # Create test client
        client = Client()
        
        # Create or get admin user
        try:
            admin_user = User.objects.get(username='admin')
            print(f"✅ Found admin user: {admin_user.username}")
        except User.DoesNotExist:
            print("❌ Admin user not found! Creating one...")
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@test.com',
                password='admin123'
            )
            print(f"✅ Created admin user: {admin_user.username}")
        
        # Test login
        login_success = client.login(username='admin', password='admin123')
        if login_success:
            print("✅ Admin login successful!")
        else:
            print("❌ Admin login failed!")
            return
        
        # Test admin panel access
        urls_to_test = [
            '/admin-panel/',
            '/admin-panel/users/',
            '/admin-panel/properties/',
            '/admin-panel/bookings/',
            '/admin-panel/analytics/',
        ]
        
        for url in urls_to_test:
            try:
                response = client.get(url)
                if response.status_code == 200:
                    print(f"✅ {url} - OK (200)")
                elif response.status_code == 302:
                    print(f"⚠️  {url} - Redirect (302) to {response.get('Location', 'unknown')}")
                elif response.status_code == 403:
                    print(f"❌ {url} - Forbidden (403)")
                else:
                    print(f"⚠️  {url} - Status {response.status_code}")
            except Exception as e:
                print(f"❌ {url} - Error: {str(e)}")
        
        # Test POST request with CSRF
        print("\n🔒 Testing CSRF Protection...")
        csrf_token = client.get('/admin-panel/').context['csrf_token']
        
        if admin_user.id:
            toggle_response = client.post(
                f'/admin-panel/users/{admin_user.id}/toggle-status/',
                HTTP_X_CSRFTOKEN=csrf_token
            )
            if toggle_response.status_code == 200:
                print("✅ CSRF protected POST request works!")
            else:
                print(f"❌ CSRF protected POST failed: {toggle_response.status_code}")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

def test_permissions():
    print("\n🔐 Testing Permission Functions...")
    
    try:
        from admin_panel.views import is_admin
        from accounts.models import User
        
        # Test admin user
        admin_user = User.objects.get(username='admin')
        if is_admin(admin_user):
            print(f"✅ is_admin() works for admin user")
        else:
            print(f"❌ is_admin() failed for admin user")
            print(f"   - is_authenticated: {admin_user.is_authenticated}")
            print(f"   - is_superuser: {admin_user.is_superuser}")
        
        # Create regular user for testing
        try:
            regular_user = User.objects.create_user(
                username='testuser',
                email='test@test.com',
                password='test123'
            )
            if not is_admin(regular_user):
                print(f"✅ is_admin() correctly denies regular user")
            else:
                print(f"❌ is_admin() incorrectly allows regular user")
            
            # Clean up
            regular_user.delete()
            
        except Exception as e:
            print(f"⚠️  Could not test regular user: {e}")
            
    except Exception as e:
        print(f"❌ Permission test failed: {str(e)}")

if __name__ == '__main__':
    print("🔧 Admin Panel Access Debugger")
    print("=" * 50)
    
    test_permissions()
    test_admin_access()
    
    print("\n🎉 Testing complete!")
    print("\n📋 If all tests pass but you still get 403:")
    print("   1. Clear browser cookies/cache")
    print("   2. Check if you're logged in as admin")
    print("   3. Restart Django server")
    print("   4. Check browser dev tools for JavaScript errors")
