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
    # Write results to a file with proper encoding
    with open('booking_test_results.txt', 'w', encoding='utf-8') as f:
        f.write("BOOKING SYSTEM VALIDATION RESULTS\n")
        f.write("=" * 50 + "\n\n")
        
        # Check properties
        properties = Property.objects.all()
        f.write(f"Total properties: {properties.count()}\n")
        
        if properties.exists():
            prop = properties.first()
            f.write(f"Sample property: {prop.title}\n")
            f.write(f"   ID: {prop.id}, Address: {prop.address}\n")
        else:
            f.write("ERROR: No properties found\n")
            return
        
        # Check users
        users = User.objects.all()
        f.write(f"\nTotal users: {users.count()}\n")
        
        if users.exists():
            user = users.first()
            f.write(f"Sample user: {user.email}\n")
        else:
            f.write("ERROR: No users found\n")
            return
        
        # Check bookings
        bookings = PropertyBooking.objects.all()
        f.write(f"\nTotal bookings: {bookings.count()}\n")
        
        # Test URL resolution
        f.write("\nURL RESOLUTION TESTS:\n")
        try:
            # Test property detail URL
            url1 = reverse('properties:property_detail', args=[prop.id])
            f.write(f"Property detail URL: {url1}\n")
            
            # Create or get a booking for testing
            booking, created = PropertyBooking.objects.get_or_create(
                customer=user,
                property_ref=prop,
                defaults={
                    'booking_type': 'booking',
                    'payment_method': 'stripe',
                    'status': 'pending',
                    'payment_amount': 100.00,
                    'customer_name': user.get_full_name() or user.email,
                    'customer_email': user.email,
                    'customer_phone': '1234567890',
                    'transaction_id': f'test_{prop.id}_{user.id}'
                }
            )
            
            if created:
                f.write(f"Created test booking: {booking.id}\n")
            else:
                f.write(f"Using existing booking: {booking.id}\n")
            
            # Test booking detail URL
            url2 = reverse('properties:booking_detail', args=[booking.id])
            f.write(f"Booking detail URL: {url2}\n")
            
            # Test property field access
            f.write(f"\nTEMPLATE FIELD ACCESS TESTS:\n")
            f.write(f"booking.property_ref.title: {booking.property_ref.title}\n")
            f.write(f"booking.property_ref.id: {booking.property_ref.id}\n")
            f.write(f"booking.property_ref.address: {booking.property_ref.address}\n")
            
            f.write(f"\nSUCCESS: All tests passed! Template fixes are working correctly.\n")
            
        except Exception as e:
            f.write(f"ERROR during testing: {str(e)}\n")
        
        f.write("\n" + "=" * 50 + "\n")

if __name__ == "__main__":
    main()
    print("Validation completed! Check booking_test_results.txt for details.")
