#!/usr/bin/env python

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_app.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def setup_admin_user():
    """Ensure admin user is properly configured"""
    print("Setting up admin user...")
    
    # Check if admin exists
    admin_email = 'admin@gmail.com'
    
    try:
        admin = User.objects.get(email=admin_email, is_superuser=True)
        print(f"✓ Found existing admin user: {admin_email}")
        
        # Update admin to ensure it has all required fields
        admin.username = admin.username or 'admin'
        admin.first_name = admin.first_name or 'Admin'
        admin.last_name = admin.last_name or 'User'
        admin.user_type = 'agent'  # Ensure user_type is set
        admin.save()
        
        print(f"✓ Updated admin user:")
        print(f"  - Username: {admin.username}")
        print(f"  - First name: {admin.first_name}")
        print(f"  - Last name: {admin.last_name}")
        print(f"  - Email: {admin.email}")
        print(f"  - User type: {admin.user_type}")
        
    except User.DoesNotExist:
        # Create new admin
        admin = User.objects.create_superuser(
            email=admin_email,
            password='admin123',
            username='admin',
            first_name='Admin',
            last_name='User',
            user_type='agent'
        )
        print(f"✓ Created new admin user: {admin_email}")
        print(f"  - Username: {admin.username}")
        print(f"  - Password: admin123")
    
    return admin

def setup_test_users():
    """Setup test users for dashboard testing"""
    print("\nSetting up test users...")
    
    # Customer user
    customer_email = 'customer@gmail.com'
    try:
        customer = User.objects.get(email=customer_email)
        print(f"✓ Found existing customer: {customer_email}")
    except User.DoesNotExist:
        customer = User.objects.create_user(
            email=customer_email,
            password='test123',
            username='customer',
            first_name='Test',
            last_name='Customer',
            user_type='customer'
        )
        print(f"✓ Created customer user: {customer_email}")
    
    # Agent user
    agent_email = 'agent@gmail.com'
    try:
        agent = User.objects.get(email=agent_email, user_type='agent', is_superuser=False)
        print(f"✓ Found existing agent: {agent_email}")
    except User.DoesNotExist:
        agent = User.objects.create_user(
            email=agent_email,
            password='test123',
            username='agent',
            first_name='Test',
            last_name='Agent',
            user_type='agent'
        )
        print(f"✓ Created agent user: {agent_email}")

if __name__ == "__main__":
    print("🔧 Setting up users for testing...")
    print("=" * 40)
    
    admin = setup_admin_user()
    setup_test_users()
    
    print("\n" + "=" * 40)
    print("✅ User setup complete!")
    print("\n🔑 Login credentials:")
    print("  Admin:    admin@gmail.com / admin123")
    print("  Customer: customer@gmail.com / test123")
    print("  Agent:    agent@gmail.com / test123")
    print("\n🌐 Test URLs:")
    print("  Admin:    http://127.0.0.1:8000/admin/")
    print("  Dashboard: http://127.0.0.1:8000/dashboard/")
