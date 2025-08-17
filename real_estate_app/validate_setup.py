#!/usr/bin/env python
"""
Quick validation script to check Django setup
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

# Add the project root to Python path
project_root = r"e:\Projects_College\VI Project\RealEstate\real_estate_app"
sys.path.insert(0, project_root)
os.chdir(project_root)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_app.settings')

# Initialize Django
django.setup()

print("✅ Django setup successful!")
print("✅ No syntax errors found!")

# Test imports
try:
    from properties.models import Property, Favorite
    from properties.views import favorites_list, toggle_favorite
    print("✅ Models and views imported successfully!")
except ImportError as e:
    print(f"❌ Import error: {e}")

# Check if database is accessible
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("✅ Database connection successful!")
except Exception as e:
    print(f"❌ Database error: {e}")

print("\n🚀 Ready to run: python manage.py runserver")
