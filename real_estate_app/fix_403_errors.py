#!/usr/bin/env python
"""
Quick fix script for 403 Forbidden errors in admin panel
"""

import os
import sys
import django

# Add the current directory to the Python path
sys.path.insert(0, os.getcwd())

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_app.settings')
django.setup()

def ensure_admin_user():
    print("👤 Ensuring admin user exists...")
    
    from accounts.models import User
    
    try:
        admin_user = User.objects.get(username='admin')
        print(f"✅ Admin user exists: {admin_user.username}")
        
        # Ensure user is superuser
        if not admin_user.is_superuser:
            admin_user.is_superuser = True
            admin_user.is_staff = True
            admin_user.save()
            print("✅ Updated admin user to superuser")
        
        # Ensure user is active
        if not admin_user.is_active:
            admin_user.is_active = True
            admin_user.save()
            print("✅ Activated admin user")
            
    except User.DoesNotExist:
        print("❌ Admin user not found! Creating...")
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@realestate.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        print(f"✅ Created admin user: {admin_user.username}")
    
    return admin_user

def check_csrf_settings():
    print("\n🔒 Checking CSRF settings...")
    
    from django.conf import settings
    
    # Check if CSRF middleware is enabled
    csrf_middleware = 'django.middleware.csrf.CsrfViewMiddleware'
    if csrf_middleware in settings.MIDDLEWARE:
        print("✅ CSRF middleware is enabled")
    else:
        print("❌ CSRF middleware is missing!")
    
    # Check CSRF settings
    csrf_settings = [
        'CSRF_COOKIE_SECURE',
        'CSRF_COOKIE_HTTPONLY', 
        'CSRF_TRUSTED_ORIGINS',
        'CSRF_FAILURE_VIEW'
    ]
    
    for setting in csrf_settings:
        value = getattr(settings, setting, 'Not set')
        print(f"   {setting}: {value}")

def check_url_patterns():
    print("\n🔗 Checking URL patterns...")
    
    try:
        from django.urls import reverse
        
        # Test critical admin URLs
        admin_urls = [
            ('admin_panel:dashboard', [], 'Dashboard'),
            ('admin_panel:users_list', [], 'Users List'),
            ('admin_panel:properties_list', [], 'Properties List'),
            ('admin_panel:bookings_list', [], 'Bookings List'),
            ('admin_panel:analytics', [], 'Analytics'),
        ]
        
        for url_name, args, description in admin_urls:
            try:
                url = reverse(url_name, args=args)
                print(f"✅ {description}: {url}")
            except Exception as e:
                print(f"❌ {description}: {str(e)}")
                
    except Exception as e:
        print(f"❌ URL pattern check failed: {str(e)}")

def create_sample_data():
    print("\n📊 Creating sample data for testing...")
    
    try:
        from accounts.models import User
        from properties.models import Property, PropertyBooking
        
        # Create sample agent if not exists
        try:
            agent = User.objects.get(username='agent1')
        except User.DoesNotExist:
            agent = User.objects.create_user(
                username='agent1',
                email='agent1@realestate.com',
                password='agent123',
                first_name='John',
                last_name='Agent',
                user_type='agent'
            )
            print(f"✅ Created sample agent: {agent.username}")
        
        # Create sample customer if not exists
        try:
            customer = User.objects.get(username='customer1')
        except User.DoesNotExist:
            customer = User.objects.create_user(
                username='customer1',
                email='customer1@realestate.com',
                password='customer123',
                first_name='Jane',
                last_name='Customer',
                user_type='customer'
            )
            print(f"✅ Created sample customer: {customer.username}")
        
        # Create sample property if not exists
        if Property.objects.count() == 0:
            property_obj = Property.objects.create(
                title='Beautiful Family Home',
                address='123 Main Street, City',
                price=500000,
                bedrooms=3,
                bathrooms=2.5,
                square_footage=2000,
                description='A lovely family home in a quiet neighborhood.',
                agent=agent,
                property_type='house',
                listing_type='sale',
                status='available'
            )
            print(f"✅ Created sample property: {property_obj.title}")
        
        print(f"📊 Current data counts:")
        print(f"   Users: {User.objects.count()}")
        print(f"   Properties: {Property.objects.count()}")
        print(f"   Bookings: {PropertyBooking.objects.count()}")
        
    except Exception as e:
        print(f"❌ Sample data creation failed: {str(e)}")

def main():
    print("🔧 Admin Panel 403 Forbidden Fix Script")
    print("=" * 50)
    
    admin_user = ensure_admin_user()
    check_csrf_settings()
    check_url_patterns()
    create_sample_data()
    
    print("\n🎉 Fix script complete!")
    print("\n📋 To resolve 403 errors:")
    print("   1. Login with: admin / admin123")
    print("   2. Ensure you're accessing: http://127.0.0.1:8000/admin-panel/")
    print("   3. Clear browser cache if needed")
    print("   4. Check browser console for JavaScript errors")
    print("   5. If problems persist, restart Django server")

if __name__ == '__main__':
    main()
