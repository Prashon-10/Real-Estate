#!/usr/bin/env python
"""
Setup booking fees for the Real Estate application
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_app.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from properties.models import BookingFee

def setup_booking_fees():
    """Create default booking fee configuration"""
    print("🔧 Setting up booking fees...")
    
    # Check if any booking fee configuration exists
    existing_fees = BookingFee.objects.filter(is_active=True).first()
    
    if existing_fees:
        print(f"✅ Active booking fees already exist:")
        print(f"   - Booking Fee: NPR {existing_fees.booking_fee}")
        print(f"   - Visit Fee: NPR {existing_fees.visit_fee}")
        return existing_fees
    
    # Create default fee configuration
    booking_fee = BookingFee.objects.create(
        booking_fee=500.00,  # NPR 500 for property booking
        visit_fee=200.00,    # NPR 200 for visit request
        is_active=True
    )
    
    print("✅ Created default booking fee configuration:")
    print(f"   - Booking Fee: NPR {booking_fee.booking_fee}")
    print(f"   - Visit Fee: NPR {booking_fee.visit_fee}")
    
    return booking_fee

if __name__ == '__main__':
    try:
        setup_booking_fees()
        print("\n🎉 Booking fees setup completed successfully!")
    except Exception as e:
        print(f"\n❌ Error setting up booking fees: {str(e)}")
        sys.exit(1)
