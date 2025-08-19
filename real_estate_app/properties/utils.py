import math
from typing import Optional, Tuple

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees) using the Haversine formula.
    
    Returns distance in kilometers.
    """
    if not all([lat1, lon1, lat2, lon2]):
        return float('inf')  # Return infinity if any coordinate is missing
    
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r

def get_properties_within_distance(center_property, max_distance_km: float = 5.0, user=None):
    """
    Get all properties by the same agent within the specified distance.
    
    Args:
        center_property: The property to calculate distance from
        max_distance_km: Maximum distance in kilometers (default: 5.0)
        user: Current user to exclude their already booked properties
    
    Returns:
        List of tuples: (property, distance_km, is_already_booked)
    """
    from .models import Property, PropertyBooking
    
    if not center_property.latitude or not center_property.longitude:
        return []
    
    # Get all properties by the same agent
    agent_properties = Property.objects.filter(
        agent=center_property.agent,
        status='available'
    ).exclude(
        id=center_property.id
    )
    
    # Get user's existing bookings for this agent if user is provided
    user_booked_property_ids = set()
    if user and user.is_authenticated:
        user_booked_property_ids = set(
            PropertyBooking.objects.filter(
                customer=user,
                property_ref__agent=center_property.agent,
                status__in=['pending', 'confirmed']
            ).values_list('property_ref_id', flat=True)
        )
    
    nearby_properties = []
    
    for property_obj in agent_properties:
        if property_obj.latitude and property_obj.longitude:
            distance = calculate_distance(
                float(center_property.latitude),
                float(center_property.longitude),
                float(property_obj.latitude),
                float(property_obj.longitude)
            )
            
            if distance <= max_distance_km:
                is_already_booked = property_obj.id in user_booked_property_ids
                nearby_properties.append((property_obj, round(distance, 2), is_already_booked))
    
    # Sort by distance
    nearby_properties.sort(key=lambda x: x[1])
    
    return nearby_properties

def check_booking_distance_compatibility(user, new_property, preferred_date) -> Tuple[bool, Optional[str], Optional[list]]:
    """
    Check if a new booking is compatible with existing bookings based on distance.
    
    Args:
        user: The user making the booking
        new_property: The property being booked
        preferred_date: The preferred date for the booking
    
    Returns:
        Tuple of (is_compatible, error_message, conflicting_bookings)
    """
    from .models import PropertyBooking
    
    # First check if user has already booked this exact property
    existing_same_property = PropertyBooking.objects.filter(
        customer=user,
        property_ref=new_property,
        status__in=['pending', 'confirmed']
    ).first()
    
    if existing_same_property:
        return False, f"You have already booked this property on {existing_same_property.preferred_date.strftime('%Y-%m-%d at %H:%M')}. You cannot book the same property multiple times.", [existing_same_property]
    
    # Get existing bookings on the same date
    existing_bookings = PropertyBooking.objects.filter(
        customer=user,
        status__in=['pending', 'confirmed'],
        preferred_date__date=preferred_date.date()
    ).exclude(property_ref=new_property)
    
    if not existing_bookings.exists():
        return True, None, []
    
    if not new_property.latitude or not new_property.longitude:
        return False, "Cannot book properties without location coordinates on the same day.", list(existing_bookings)
    
    conflicting_bookings = []
    
    for booking in existing_bookings:
        existing_property = booking.property_ref
        
        if not existing_property.latitude or not existing_property.longitude:
            conflicting_bookings.append(booking)
            continue
        
        distance = calculate_distance(
            float(new_property.latitude),
            float(new_property.longitude),
            float(existing_property.latitude),
            float(existing_property.longitude)
        )
        
        if distance > 5.0:  # More than 5km apart
            conflicting_bookings.append(booking)
    
    if conflicting_bookings:
        error_msg = "You cannot book properties that are more than 5km apart on the same day. "
        error_msg += f"The following booking(s) conflict: "
        
        conflict_details = []
        for booking in conflicting_bookings:
            existing_property = booking.property_ref
            if existing_property.latitude and existing_property.longitude and new_property.latitude and new_property.longitude:
                distance = calculate_distance(
                    float(new_property.latitude),
                    float(new_property.longitude),
                    float(existing_property.latitude),
                    float(existing_property.longitude)
                )
                conflict_details.append(f"'{existing_property.title}' ({distance:.2f}km away)")
            else:
                conflict_details.append(f"'{existing_property.title}' (location unknown)")
        
        error_msg += ", ".join(conflict_details)
        return False, error_msg, conflicting_bookings
    
    return True, None, []
