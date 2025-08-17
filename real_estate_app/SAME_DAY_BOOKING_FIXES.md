# Same-Day Booking Logic Fixes

## Issues Fixed

### Issue 1: Visit Fee Discount Logic ✅ 
**Problem**: Visit price reduction was applying incorrectly
**Solution**: Already correctly implemented - discount only applies for same agent bookings

**Current Logic**:
```python
# Get previous bookings with the same agent
query = PropertyBooking.objects.filter(
    customer=self.user,
    property_ref__agent=self.current_property.agent,  # Same agent only
    status__in=['pending', 'confirmed'],
    preferred_date__isnull=False
)
```

**Result**: 
- Visit with same agent (repeat customer): NPR 250.00 ✅
- Visit with different agent: NPR 500.00 ✅

### Issue 2: Same-Day Booking Restrictions ✅
**Problem**: Users couldn't book with different agents on same day
**Solution**: Modified distance compatibility check

**Before**:
```python
# Blocked ALL same-day bookings regardless of agent
existing_bookings = PropertyBooking.objects.filter(
    customer=user,
    status__in=['pending', 'confirmed'],
    preferred_date__date=preferred_date.date()
)
# Applied 5km restriction to ALL bookings
```

**After**:
```python
# Allow bookings with different agents without distance restrictions
if existing_property.agent != new_property.agent:
    continue  # No conflict for different agents

# Only apply 5km restriction for same agent
if distance > 5.0:  # More than 5km apart
    conflicting_bookings.append(booking)
```

**Result**:
- ✅ Can book with different agents on same day
- ✅ 5km restriction only applies to same agent properties  
- ✅ Backend and frontend validation updated

## Updated Business Logic

### Same-Day Booking Rules:
1. **Different Agents**: ✅ Allowed (no distance restrictions)
2. **Same Agent**: ✅ Allowed if within 5km
3. **Same Agent**: ❌ Blocked if more than 5km apart

### Visit Fee Structure:
1. **First visit with agent**: NPR 500.00
2. **Repeat visit with same agent**: NPR 250.00  
3. **Visit with different agent**: NPR 500.00 (no discount)

### Frontend Improvements:
- Smart conflict detection based on agent
- Different messages for same vs different agents
- User confirmation for different agent bookings

## Files Modified:
1. `properties/utils.py` - Updated distance compatibility logic
2. `properties/booking_views.py` - Added current agent context  
3. `templates/properties/booking_form.html` - Enhanced frontend validation

## Testing Scenarios:
- ✅ Book visit with Agent A (NPR 500.00)
- ✅ Book another visit with Agent A same day - checks distance
- ✅ Book visit with Agent B same day - allowed without distance check  
- ✅ Book repeat visit with Agent A different day (NPR 250.00)
- ✅ Book visit with Agent B (NPR 500.00, no discount from Agent A history)
