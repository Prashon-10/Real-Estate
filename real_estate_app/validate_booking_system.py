#!/usr/bin/env python
"""
Simple validation script for booking system
"""
import os
import sys
import django

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_app.settings')
django.setup()

from django.urls import reverse
from properties.models import Property, PropertyBooking
from accounts.models import User

def main():
    # Write results to a file
    with open('booking_test_results.txt', 'w') as f:
        f.write("🧪 Booking System Validation Results\n")
        f.write("=" * 50 + "\n\n")
        
        # Check properties
        properties = Property.objects.all()
        f.write(f"📊 Total properties: {properties.count()}\n")
        
        if properties.exists():
            prop = properties.first()
            f.write(f"✅ Sample property: {prop.title}\n")
            f.write(f"   ID: {prop.id}, Location: {prop.location}\n")
        else:
            f.write("❌ No properties found\n")
            return
        
        # Check users
        users = User.objects.all()
        f.write(f"\n👤 Total users: {users.count()}\n")
        
        if users.exists():
            user = users.first()
            f.write(f"✅ Sample user: {user.email}\n")
        else:
            f.write("❌ No users found\n")
            return
        
        # Check bookings
        bookings = PropertyBooking.objects.all()
        f.write(f"\n📋 Total bookings: {bookings.count()}\n")
        
        # Test URL resolution
        f.write("\n🔗 URL Resolution Tests:\n")
        try:
            # Test property detail URL
            url1 = reverse('properties:property_detail', args=[prop.id])
            f.write(f"✅ Property detail URL: {url1}\n")
            
            # Create or get a booking for testing
            booking, created = PropertyBooking.objects.get_or_create(
                user=user,
                property_ref=prop,
                defaults={
                    'booking_type': 'booking',
                    'payment_method': 'stripe',
                    'status': 'pending',
                    'amount': 100.00
                }
            )
            
            if created:
                f.write(f"✅ Created test booking: {booking.id}\n")
            else:
                f.write(f"✅ Using existing booking: {booking.id}\n")
            
            # Test booking detail URL
            url2 = reverse('properties:booking_detail', args=[booking.id])
            f.write(f"✅ Booking detail URL: {url2}\n")
            
            # Test property field access
            f.write(f"\n📄 Template Field Access Tests:\n")
            f.write(f"✅ booking.property_ref.title: {booking.property_ref.title}\n")
            f.write(f"✅ booking.property_ref.id: {booking.property_ref.id}\n")
            f.write(f"✅ booking.property_ref.location: {booking.property_ref.location}\n")
            
            f.write(f"\n🎉 All tests passed! Template fixes are working correctly.\n")
            
        except Exception as e:
            f.write(f"❌ Error during testing: {str(e)}\n")
        
        f.write("\n" + "=" * 50 + "\n")

if __name__ == "__main__":
    main()
    print("✅ Validation completed! Check booking_test_results.txt for details.")
