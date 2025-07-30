#!/usr/bin/env python
"""
Database setup and migration script
"""

import os
import sys
import django
import subprocess

# Add the current directory to the Python path
sys.path.insert(0, os.getcwd())

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_app.settings')

def run_command(command):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🔧 Setting up RealEstate Database...")
    
    # Check Django setup
    try:
        django.setup()
        print("✅ Django setup successful!")
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return
    
    # Run migrations
    print("\n📦 Running database migrations...")
    success, stdout, stderr = run_command("python manage.py makemigrations")
    if success:
        print("✅ Migrations created successfully!")
    else:
        print(f"⚠️  Migration creation: {stderr}")
    
    success, stdout, stderr = run_command("python manage.py migrate")
    if success:
        print("✅ Database migrated successfully!")
    else:
        print(f"❌ Migration failed: {stderr}")
        return
    
    # Create superuser if needed
    print("\n👤 Checking for admin user...")
    from accounts.models import User
    
    try:
        admin_user = User.objects.get(username='admin')
        print(f"✅ Admin user already exists: {admin_user.username}")
    except User.DoesNotExist:
        print("📝 Creating admin user...")
        try:
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@realestate.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            print(f"✅ Admin user created: {admin_user.username}")
        except Exception as e:
            print(f"❌ Failed to create admin user: {e}")
            return
    
    # Collect static files
    print("\n📁 Collecting static files...")
    success, stdout, stderr = run_command("python manage.py collectstatic --noinput")
    if success:
        print("✅ Static files collected!")
    else:
        print(f"⚠️  Static files collection: {stderr}")
    
    print("\n🎉 Database setup complete!")
    print("\n📋 Summary:")
    print("   - Database migrated")
    print("   - Admin user: admin / admin123") 
    print("   - Static files collected")
    print("\n🚀 You can now run: python manage.py runserver")
    print("🌐 Admin Panel: http://127.0.0.1:8000/admin-panel/")

if __name__ == '__main__':
    main()
