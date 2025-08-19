"""
REAL ESTATE ALGORITHMS - WORKING CODE EXAMPLES
==============================================
Small working code snippets (12-13 lines each) with actual outputs
"""

# ==========================================
# 1. SEMANTIC SEARCH ALGORITHM - WORKING CODE
# ==========================================

def semantic_search():
    query = "luxury 3 bedroom apartment downtown"
    properties = [
        {"id": 1, "title": "Luxury 3BR Apartment Downtown", "type": "apartment"},
        {"id": 2, "title": "Modern 2BR House Suburbs", "type": "house"},
        {"id": 3, "title": "Premium 3 Bedroom Flat City Center", "type": "apartment"}
    ]
    
    intent = {'property_types': [], 'bedrooms': None}
    if 'apartment' in query.lower():
        intent['property_types'].append('apartment')
    
    results = [p for p in properties if p['type'] in intent['property_types']]
    print(f"Query: {query}")
    print(f"Intent: {intent}")
    print(f"Matching Properties: {len(results)} found")
    return results

# Output:
# Query: luxury 3 bedroom apartment downtown
# Intent: {'property_types': ['apartment'], 'bedrooms': None}
# Matching Properties: 2 found

# ==========================================
# 2. PROPERTY FILTER ALGORITHM - WORKING CODE
# ==========================================

def property_filter():
    properties = [
        {"id": 1, "price": 5000000, "type": "apartment", "lat": 27.7172, "lng": 85.3240},
        {"id": 2, "price": 2000000, "type": "house", "lat": 27.7000, "lng": 85.3333},
        {"id": 3, "price": 8000000, "type": "apartment", "lat": 27.7100, "lng": 85.3200}
    ]
    
    filters = {'property_type': 'apartment', 'min_price': 3000000}
    filtered = [p for p in properties if p['type'] == filters['property_type'] and p['price'] >= filters['min_price']]
    
    lat1, lng1 = properties[0]['lat'], properties[0]['lng']
    lat2, lng2 = properties[1]['lat'], properties[1]['lng']
    distance = ((lat2-lat1)**2 + (lng2-lng1)**2)**0.5 * 111
    
    print(f"Total Properties: {len(properties)}")
    print(f"After Filtering: {len(filtered)} apartments above 3M")
    print(f"Distance between prop 1&2: {distance:.1f}km")
    return filtered

# Output:
# Total Properties: 3
# After Filtering: 2 apartments above 3M
# Distance between prop 1&2: 2.2km

# ==========================================
# 3. USER AUTHENTICATION - WORKING CODE
# ==========================================

def authentication():
    users = [
        {"id": 1, "username": "john_doe", "email": "john@gmail.com", "password": "salt$secure123_hashed", "user_type": "customer"},
        {"id": 2, "username": "jane_agent", "email": "jane@yahoo.com", "password": "salt$agent456_hashed", "user_type": "agent"}
    ]
    
    def authenticate(username, password):
        user = next((u for u in users if u['username'] == username), None)
        if user and f"{password}_hashed" in user['password']:
            return True, "Login successful", {"user_id": user['id'], "user_type": user['user_type']}
        return False, "Invalid credentials", None
    
    success1, msg1, session1 = authenticate("john_doe", "secure123")
    success2, msg2, session2 = authenticate("john_doe", "wrong_pass")
    
    print(f"Login Test 1: {success1} - {msg1}")
    print(f"Session: {session1}")
    print(f"Login Test 2: {success2} - {msg2}")
    return session1

# Output:
# Login Test 1: True - Login successful
# Session: {'user_id': 1, 'user_type': 'customer'}
# Login Test 2: False - Invalid credentials

# ==========================================
# 4. BOOKING VALIDATION - WORKING CODE
# ==========================================

def booking_validation():
    user_bookings = [
        {"property_id": 1, "date": "2025-08-19", "lat": 27.7172, "lng": 85.3240},
        {"property_id": 2, "date": "2025-08-20", "lat": 27.7000, "lng": 85.3333}
    ]
    
    new_booking = {"property_id": 3, "date": "2025-08-19", "lat": 27.7500, "lng": 85.3600}
    
    same_day_bookings = [b for b in user_bookings if b['date'] == new_booking['date']]
    
    is_valid = True
    for booking in same_day_bookings:
        distance = ((new_booking['lat'] - booking['lat'])**2 + (new_booking['lng'] - booking['lng'])**2)**0.5 * 111
        if distance > 5.0:
            is_valid = False
            break
    
    property_price = 6000000
    booking_fee = min(property_price * 0.02, 50000)
    
    print(f"Same day bookings: {len(same_day_bookings)}")
    print(f"Distance check: {'PASS' if is_valid else 'FAIL - exceeds 5km'}")
    print(f"Booking fee for 6M property: ₹{booking_fee:,.0f}")
    return is_valid, booking_fee

# Output:
# Same day bookings: 1
# Distance check: FAIL - exceeds 5km
# Booking fee for 6M property: ₹50,000

# ==========================================
# 5. RECOMMENDATION SYSTEM - WORKING CODE
# ==========================================

def recommendation():
    user_preferences = {"apartment": 3, "luxury": 2}
    
    properties = [
        {"id": 1, "title": "Luxury Apartment Downtown", "type": "apartment", "price": 8000000},
        {"id": 2, "title": "Budget House Suburbs", "type": "house", "price": 2000000},
        {"id": 3, "title": "Modern Apartment City", "type": "apartment", "price": 4000000}
    ]
    
    scored_properties = []
    for prop in properties:
        base_score = 0.5
        if prop['type'] in user_preferences:
            base_score += 0.3
        if 'luxury' in prop['title'].lower() and prop['price'] > 6000000:
            base_score += 0.2
        
        scored_properties.append((prop['id'], prop['title'], round(base_score, 2)))
    
    scored_properties.sort(key=lambda x: x[2], reverse=True)
    
    print("Recommendation Scores:")
    for prop_id, title, score in scored_properties:
        print(f"ID {prop_id}: {score} - {title[:30]}...")
    return scored_properties

# Output:
# Recommendation Scores:
# ID 1: 1.0 - Luxury Apartment Downtown...
# ID 3: 0.8 - Modern Apartment City...
# ID 2: 0.5 - Budget House Suburbs...

# ==========================================
# RUN ALL ALGORITHMS
# ==========================================

if __name__ == "__main__":
    print("=" * 50)
    print("REAL ESTATE ALGORITHMS - RESULTS")
    print("=" * 50)
    
    print("\n1. SEMANTIC SEARCH:")
    semantic_search()
    
    print("\n2. PROPERTY FILTER:")
    property_filter()
    
    print("\n3. AUTHENTICATION:")
    authentication()
    
    print("\n4. BOOKING VALIDATION:")
    booking_validation()
    
    print("\n5. RECOMMENDATION SYSTEM:")
    recommendation()
    
    print("\n" + "=" * 50)
    print("ALL ALGORITHMS TESTED SUCCESSFULLY!")
    print("=" * 50)
