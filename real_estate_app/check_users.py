#!/usr/bin/env python
"""
Check user data to identify name mismatch issue
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_app.settings')
django.setup()

from accounts.models import User

def check_user_data():
    """Check all users to identify name issues"""
    agents = User.objects.filter(user_type='agent')
    
    print("=== AGENT USERS ANALYSIS ===")
    print(f"Found {agents.count()} agents")
    print()
    
    for user in agents:
        print(f"User ID: {user.id}")
        print(f"Username: {user.username}")
        print(f"First Name: '{user.first_name}'")
        print(f"Last Name: '{user.last_name}'")
        print(f"Email: {user.email}")
        print(f"Full Name: '{user.get_full_name()}'")
        print(f"User Type: {user.user_type}")
        print("-" * 50)
        
    # Look for specific patterns
    print("\n=== POTENTIAL ISSUES ===")
    for user in agents:
        if user.first_name and user.get_full_name() != user.first_name:
            print(f"MISMATCH: {user.username}")
            print(f"  - First name: '{user.first_name}'")
            print(f"  - Full name: '{user.get_full_name()}'")
            print(f"  - Last name: '{user.last_name}'")
        
        if not user.first_name and not user.last_name:
            print(f"NO NAMES SET: {user.username}")
            print(f"  - Using email/username for display")

if __name__ == "__main__":
    check_user_data()
