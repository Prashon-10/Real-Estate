#!/usr/bin/env python3
"""
Create a test booking to verify booking prevention functionality
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.append('.')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_app.settings')
django.setup()

from django.contrib.auth import get_user_model
from properties.models import Property, PropertyBooking
from datetime import datetime, timedelta
import uuid

User = get_user_model()

def create_test_booking():
    print("🧪 Creating Test Booking for Prevention Test")
    print("=" * 50)
    
    # Get a customer user
    customer = User.objects.filter(user_type='customer').first()
    if not customer:
        print("❌ No customer found")
        return
    
    print(f"✅ Using customer: {customer.username}")
    
    # Get a property
    property = Property.objects.filter(status='available').first()
    if not property:
        print("❌ No available properties found")
        return
    
    print(f"✅ Using property: {property.title}")
    
    # Check if booking already exists
    existing_booking = PropertyBooking.objects.filter(
        customer=customer,
        property_ref=property,
        status__in=['pending', 'confirmed']
    ).first()
    
    if existing_booking:
        print(f"✅ Booking already exists: ID {existing_booking.id}, Status: {existing_booking.status}")
        return existing_booking
    
    # Create a test booking
    booking = PropertyBooking.objects.create(
        property_ref=property,
        customer=customer,
        booking_type='booking',
        customer_name=customer.get_full_name() or customer.username,
        customer_email=customer.email,
        customer_phone='9800000000',
        preferred_date=datetime.now() + timedelta(days=7),
        message='Test booking for prevention functionality',
        payment_method='esewa',
        transaction_id=f'TEST_{uuid.uuid4().hex[:8].upper()}',
        payment_amount=10000.00,
        payment_status='completed',
        status='pending'
    )
    
    print(f"✅ Created test booking:")
    print(f"   - Booking ID: {booking.id}")
    print(f"   - Customer: {booking.customer.username}")
    print(f"   - Property: {booking.property_ref.title}")
    print(f"   - Status: {booking.status}")
    print(f"   - Type: {booking.booking_type}")
    print(f"   - Transaction ID: {booking.transaction_id}")
    
    print("\n" + "=" * 50)
    print("✅ Test booking created successfully!")
    print("\nNow check the property listing and detail pages:")
    print("1. This property should now show 'Already Booked' buttons")
    print("2. Other properties should still show normal booking buttons")
    print("3. The disabled buttons should not be clickable")
    
    return booking

if __name__ == "__main__":
    create_test_booking()
