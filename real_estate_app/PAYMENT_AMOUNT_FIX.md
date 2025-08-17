# Payment Amount Fix Summary

## Problem
The booking form was showing NPR 250.0 for property booking instead of the correct NPR 5000.0 booking fee. The payment calculation was not properly distinguishing between booking fees and visit fees.

## Root Cause Analysis
1. **Form calculation issue**: The `_calculate_payment_amount` method in `PropertyBookingForm` was using a hardcoded base amount of 500.00 for all booking types
2. **Fee structure mismatch**: The method wasn't using the actual `BookingFee` model values
3. **Incorrect fee assignment**: The view was only updating visit fees but not booking fees in the context

## Fixes Applied

### 1. Fixed Payment Calculation Logic (`properties/booking_forms.py`)
**Before**:
```python
def _calculate_payment_amount(self, booking_type='visit', preferred_date=None):
    # Base amount is Rs. 500 for first-time bookings
    base_amount = 500.00
    # ... discount logic applied to all types
```

**After**:
```python
def _calculate_payment_amount(self, booking_type='visit', preferred_date=None):
    # Get current fees from BookingFee model
    from .models import BookingFee
    current_fees = BookingFee.get_current_fees()
    
    # Base amount depends on booking type
    if booking_type == 'booking':
        base_amount = float(current_fees['booking_fee'])  # NPR 5000.00
    else:  # visit
        base_amount = float(current_fees['visit_fee'])    # NPR 250.00
    
    # Apply discount only to visits for repeat customers
    if booking_type == 'visit' and has_previous_bookings:
        base_amount = 250.00  # Repeat customer visit discount
```

### 2. Updated View Context (`properties/booking_views.py`)
**Before**:
```python
fees = BookingFee.get_current_fees()
actual_visit_fee = form.get_initial_payment_amount('visit')
fees['visit_fee'] = actual_visit_fee
```

**After**:
```python
fees = BookingFee.get_current_fees()
actual_visit_fee = form.get_initial_payment_amount('visit')
actual_booking_fee = form.get_initial_payment_amount('booking')
fees['visit_fee'] = actual_visit_fee
fees['booking_fee'] = actual_booking_fee
```

### 3. Database Fee Configuration
The system should have:
- **Property Booking Fee**: NPR 5000.00
- **Property Visit Fee**: NPR 250.00

## Expected Behavior After Fix

### Booking Form Display
- **Property Booking option**: Shows "NPR 5000.00" (or configured booking_fee)
- **Property Visit option**: Shows "NPR 250.00" (or configured visit_fee)

### Payment Page
- **Property Booking**: Payment Amount should be NPR 5000.00
- **Property Visit**: Payment Amount should be NPR 250.00

### Repeat Customer Logic
- **Booking fees**: Always use full booking_fee (no discount)
- **Visit fees**: Use visit_fee, with potential discount to NPR 250.00 for repeat customers

## Testing Steps
1. Navigate to property booking page
2. Select "Property Booking" → Should show NPR 5000.00 fee
3. Proceed to payment → Should show NPR 5000.00 payment amount
4. Go back and select "Property Visit" → Should show NPR 250.00 fee  
5. Proceed to payment → Should show NPR 250.00 payment amount

## Files Modified
1. `properties/booking_forms.py` - Fixed payment calculation logic
2. `properties/booking_views.py` - Updated context fee assignment
3. `test_payment_calculation.py` - Created test script for verification
4. `check_and_update_fees.py` - Created fee configuration script

## Verification Commands
```bash
# Test payment calculation
python test_payment_calculation.py

# Check/update fee configuration  
python check_and_update_fees.py

# Django shell verification
python manage.py shell -c "
from properties.models import BookingFee;
from properties.booking_forms import PropertyBookingForm;
print('Current fees:', BookingFee.get_current_fees());
form = PropertyBookingForm();
print('Booking amount:', form._calculate_payment_amount('booking'));
print('Visit amount:', form._calculate_payment_amount('visit'));
"
```

The payment amount should now correctly show NPR 5000.00 for property bookings and NPR 250.00 for property visits! 🎉
