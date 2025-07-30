#!/usr/bin/env python
"""
Quick Django check script
"""

import os
import sys
import django

# Add the current directory to the Python path
sys.path.insert(0, os.getcwd())

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_app.settings')

try:
    django.setup()
    print("✅ Django setup successful!")
    
    # Test imports
    from admin_panel.views import admin_dashboard
    print("✅ Admin panel views import successful!")
    
    from admin_panel.urls import urlpatterns
    print("✅ Admin panel URLs import successful!")
    
    from accounts.models import User
    from properties.models import Property, PropertyBooking
    print("✅ Model imports successful!")
    
    print("\n🎉 All imports working correctly!")
    print("🚀 You can now run: python manage.py runserver")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
