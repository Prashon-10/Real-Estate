#!/usr/bin/env python
"""
Create test bookings to verify grayed-out property functionality
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_app.settings')
django.setup()

from properties.models import Property, PropertyBooking
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

def create_test_bookings():
    """Create test bookings to demonstrate grayed-out functionality"""
    
    print("🏠 Creating test bookings for grayed-out property demonstration...")
    print("=" * 70)
    
    # Get some properties and users
    properties = Property.objects.filter(status='available')[:3]
    customers = User.objects.filter(user_type='customer')[:2]
    
    if not properties.exists():
        print("❌ No available properties found!")
        return
    
    if not customers.exists():
        print("❌ No customers found!")
        return
    
    # Create confirmed booking (should gray out property)
    if properties.count() >= 1 and customers.count() >= 1:
        property1 = properties[0]
        customer1 = customers[0]
        
        booking1, created = PropertyBooking.objects.get_or_create(
            property_ref=property1,
            customer=customer1,
            booking_type='booking',  # This is an actual BOOKING
            defaults={
                'customer_name': customer1.get_full_name() or customer1.username,
                'customer_email': customer1.email,
                'customer_phone': '1234567890',
                'payment_method': 'stripe',
                'transaction_id': f'test_booking_{datetime.now().timestamp()}',
                'payment_amount': Decimal('1000.00'),
                'status': 'confirmed',  # This should gray out the property
                'message': 'Test confirmed booking for graying out'
            }
        )
        
        if created:
            print(f"✅ Created CONFIRMED BOOKING for property '{property1.title}'")
            print(f"   Customer: {customer1.get_full_name() or customer1.username}")
            print(f"   Type: {booking1.booking_type}")
            print(f"   Status: {booking1.status}")
            print(f"   ➡️  This property should be GRAYED OUT for other users")
        else:
            print(f"ℹ️  Booking already exists for property '{property1.title}'")
    
    # Create confirmed visit (should NOT gray out property)
    if properties.count() >= 2 and customers.count() >= 1:
        property2 = properties[1]
        customer1 = customers[0]
        
        visit1, created = PropertyBooking.objects.get_or_create(
            property_ref=property2,
            customer=customer1,
            booking_type='visit',  # This is just a VISIT
            defaults={
                'customer_name': customer1.get_full_name() or customer1.username,
                'customer_email': customer1.email,
                'customer_phone': '1234567890',
                'payment_method': 'stripe',
                'transaction_id': f'test_visit_{datetime.now().timestamp()}',
                'payment_amount': Decimal('50.00'),
                'status': 'confirmed',  # Even though confirmed, it's just a visit
                'message': 'Test confirmed visit - should NOT gray out property',
                'preferred_date': datetime.now() + timedelta(days=7)
            }
        )
        
        if created:
            print(f"\n✅ Created CONFIRMED VISIT for property '{property2.title}'")
            print(f"   Customer: {customer1.get_full_name() or customer1.username}")
            print(f"   Type: {visit1.booking_type}")
            print(f"   Status: {visit1.status}")
            print(f"   ➡️  This property should NOT be grayed out (visit only)")
        else:
            print(f"\nℹ️  Visit already exists for property '{property2.title}'")
    
    # Create pending booking (should NOT gray out property)
    if properties.count() >= 3 and customers.count() >= 2:
        property3 = properties[2]
        customer2 = customers[1]
        
        booking2, created = PropertyBooking.objects.get_or_create(
            property_ref=property3,
            customer=customer2,
            booking_type='booking',  # This is a BOOKING
            defaults={
                'customer_name': customer2.get_full_name() or customer2.username,
                'customer_email': customer2.email,
                'customer_phone': '0987654321',
                'payment_method': 'esewa',
                'transaction_id': f'test_pending_{datetime.now().timestamp()}',
                'payment_amount': Decimal('1500.00'),
                'status': 'pending',  # Pending, so should NOT gray out
                'message': 'Test pending booking - should NOT gray out property'
            }
        )
        
        if created:
            print(f"\n✅ Created PENDING BOOKING for property '{property3.title}'")
            print(f"   Customer: {customer2.get_full_name() or customer2.username}")
            print(f"   Type: {booking2.booking_type}")
            print(f"   Status: {booking2.status}")
            print(f"   ➡️  This property should NOT be grayed out (pending only)")
        else:
            print(f"\nℹ️  Pending booking already exists for property '{property3.title}'")
    
    print("\n" + "=" * 70)
    print("🎯 Summary:")
    
    # Check which properties should be grayed out
    grayed_out_properties = PropertyBooking.objects.filter(
        booking_type='booking',
        status='confirmed'
    ).values_list('property_ref__title', flat=True)
    
    print(f"Properties that should be GRAYED OUT: {list(grayed_out_properties)}")
    
    # Properties with other statuses/types
    not_grayed_out = Property.objects.exclude(
        id__in=PropertyBooking.objects.filter(
            booking_type='booking',
            status='confirmed'
        ).values_list('property_ref__id', flat=True)
    ).values_list('title', flat=True)[:5]
    
    print(f"Properties that should NOT be grayed out: {list(not_grayed_out)}")
    
    print("\n🌐 You can now visit the property list page to see the grayed-out effect!")
    print("   Grayed-out properties will have reduced opacity and a 'BOOKED' overlay.")

if __name__ == "__main__":
    create_test_bookings()
