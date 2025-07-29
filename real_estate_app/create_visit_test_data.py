#!/usr/bin/env python
"""
Test script to verify visit request indicators and blocked dates functionality
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

def create_visit_test_data():
    """Create test visit requests to demonstrate new functionality"""
    
    print("🏠 Creating test visit requests for demonstration...")
    print("=" * 70)
    
    # Get some properties and customers
    properties = Property.objects.filter(status='available')[:3]
    customers = User.objects.filter(user_type='customer')[:2]
    
    if not properties.exists():
        print("❌ No available properties found!")
        return
    
    if not customers.exists():
        print("❌ No customers found!")
        return
    
    # Create confirmed visit request (should show "Being Visited" indicator)
    if properties.count() >= 1 and customers.count() >= 1:
        property1 = properties[0]
        customer1 = customers[0]
        
        visit_date1 = datetime.now() + timedelta(days=5)
        
        visit1, created = PropertyBooking.objects.get_or_create(
            property_ref=property1,
            customer=customer1,
            booking_type='visit',  # This is a VISIT REQUEST
            defaults={
                'customer_name': customer1.get_full_name() or customer1.username,
                'customer_email': customer1.email,
                'customer_phone': '1234567890',
                'payment_method': 'stripe',
                'transaction_id': f'test_visit_{datetime.now().timestamp()}',
                'payment_amount': Decimal('50.00'),
                'status': 'confirmed',  # Confirmed visit
                'message': 'Test confirmed visit for "Being Visited" indicator',
                'preferred_date': visit_date1
            }
        )
        
        if created:
            print(f"✅ Created CONFIRMED VISIT for property '{property1.title}'")
            print(f"   Customer: {customer1.get_full_name() or customer1.username}")
            print(f"   Visit Date: {visit_date1.strftime('%Y-%m-%d %H:%M')}")
            print(f"   Status: {visit1.status}")
            print(f"   ➡️  This property should show 'BEING VISITED' indicator")
        else:
            print(f"ℹ️  Visit already exists for property '{property1.title}'")
    
    # Create another visit request for same property (different date)
    if properties.count() >= 1 and customers.count() >= 2:
        property1 = properties[0]
        customer2 = customers[1] if customers.count() > 1 else customers[0]
        
        visit_date2 = datetime.now() + timedelta(days=7)
        
        visit2, created = PropertyBooking.objects.get_or_create(
            property_ref=property1,
            customer=customer2,
            booking_type='visit',
            defaults={
                'customer_name': customer2.get_full_name() or customer2.username,
                'customer_email': customer2.email,
                'customer_phone': '0987654321',
                'payment_method': 'esewa',
                'transaction_id': f'test_visit2_{datetime.now().timestamp()}',
                'payment_amount': Decimal('50.00'),
                'status': 'pending',  # Pending visit
                'message': 'Second visit request for blocked dates test',
                'preferred_date': visit_date2
            }
        )
        
        if created:
            print(f"\n✅ Created PENDING VISIT for same property")
            print(f"   Customer: {customer2.get_full_name() or customer2.username}")
            print(f"   Visit Date: {visit_date2.strftime('%Y-%m-%d %H:%M')}")
            print(f"   Status: {visit2.status}")
            print(f"   ➡️  This date should be BLOCKED for other users")
        else:
            print(f"\nℹ️  Second visit already exists")
    
    # Create visit request for different property
    if properties.count() >= 2:
        property2 = properties[1]
        customer1 = customers[0]
        
        visit_date3 = datetime.now() + timedelta(days=3)
        
        visit3, created = PropertyBooking.objects.get_or_create(
            property_ref=property2,
            customer=customer1,
            booking_type='visit',
            defaults={
                'customer_name': customer1.get_full_name() or customer1.username,
                'customer_email': customer1.email,
                'customer_phone': '1234567890',
                'payment_method': 'stripe',
                'transaction_id': f'test_visit3_{datetime.now().timestamp()}',
                'payment_amount': Decimal('50.00'),
                'status': 'confirmed',
                'message': 'Visit request for another property',
                'preferred_date': visit_date3
            }
        )
        
        if created:
            print(f"\n✅ Created VISIT for property '{property2.title}'")
            print(f"   Visit Date: {visit_date3.strftime('%Y-%m-%d %H:%M')}")
            print(f"   ➡️  Another property with visit indicator")
    
    print("\n" + "=" * 70)
    print("🎯 Summary of New Features:")
    
    # Properties with visit requests (should show "Being Visited")
    visited_properties = PropertyBooking.objects.filter(
        booking_type='visit',
        status__in=['pending', 'confirmed']
    ).values_list('property_ref__title', flat=True).distinct()
    
    print(f"Properties with 'BEING VISITED' indicator: {list(visited_properties)}")
    
    # All blocked dates
    blocked_dates = PropertyBooking.objects.filter(
        booking_type='visit',
        status__in=['pending', 'confirmed'],
        preferred_date__isnull=False
    ).values_list('property_ref__title', 'preferred_date')
    
    print(f"\nBlocked visit dates:")
    for property_title, blocked_date in blocked_dates:
        print(f"  - {property_title}: {blocked_date.strftime('%Y-%m-%d %H:%M')}")
    
    print("\n🌟 New Visual Features:")
    print("1. Properties with visit requests show '👁️ BEING VISITED' indicator")
    print("2. Visit request count shown on property detail page")
    print("3. Date picker blocks already selected dates")
    print("4. Clean separation between bookings and visits")
    print("\n🌐 Visit the property list and booking pages to see the new features!")

if __name__ == "__main__":
    create_visit_test_data()
