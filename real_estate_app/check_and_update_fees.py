#!/usr/bin/env python3
"""
Script to check and update booking fees in the system
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_app.settings')
django.setup()

from properties.models import BookingFee

def check_and_update_fees():
    """Check current fees and update them if needed"""
    
    print("🔍 Checking current booking fees...")
    print("=" * 50)
    
    # Get current fees
    current_fees = BookingFee.get_current_fees()
    print(f"Current booking fee: NPR {current_fees['booking_fee']}")
    print(f"Current visit fee: NPR {current_fees['visit_fee']}")
    
    # Check if there's an active BookingFee record
    active_fee_config = BookingFee.objects.filter(is_active=True).first()
    
    if active_fee_config:
        print(f"\n✅ Found active fee configuration:")
        print(f"   - Booking fee: NPR {active_fee_config.booking_fee}")
        print(f"   - Visit fee: NPR {active_fee_config.visit_fee}")
        print(f"   - Created: {active_fee_config.created_at}")
    else:
        print("\n⚠️  No active fee configuration found. Creating default configuration...")
        
        # Create default configuration with proper fees
        BookingFee.objects.create(
            booking_fee=5000.00,  # NPR 5000 for property booking
            visit_fee=250.00,     # NPR 250 for property visit
            is_active=True
        )
        print("✅ Created default fee configuration:")
        print("   - Booking fee: NPR 5000.00")
        print("   - Visit fee: NPR 250.00")
    
    # Check if fees need updating
    if active_fee_config and (active_fee_config.booking_fee != 5000.00 or active_fee_config.visit_fee != 250.00):
        print(f"\n🔄 Updating fees to correct values...")
        
        # Deactivate current config
        active_fee_config.is_active = False
        active_fee_config.save()
        
        # Create new config with correct fees
        new_config = BookingFee.objects.create(
            booking_fee=5000.00,  # Property booking fee
            visit_fee=250.00,     # Property visit fee  
            is_active=True
        )
        
        print("✅ Updated fee configuration:")
        print(f"   - Booking fee: NPR {new_config.booking_fee}")
        print(f"   - Visit fee: NPR {new_config.visit_fee}")
    
    # Final verification
    print("\n" + "=" * 50)
    final_fees = BookingFee.get_current_fees()
    print("🎉 Final fee configuration:")
    print(f"   - Property Booking: NPR {final_fees['booking_fee']}")
    print(f"   - Property Visit: NPR {final_fees['visit_fee']}")
    
    return True

if __name__ == "__main__":
    check_and_update_fees()
