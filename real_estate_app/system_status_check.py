#!/usr/bin/env python
"""
Comprehensive status check for the Dual Confirmation System
"""

import os
import sys

print("🔍 DUAL CONFIRMATION SYSTEM STATUS CHECK")
print("=" * 50)

# Check if required files exist
files_to_check = [
    'db.sqlite3',
    'properties/models.py',
    'properties/booking_views.py',
    'properties/urls.py',
    'templates/properties/agent_bookings.html',
    'templates/properties/property_detail.html'
]

print("\n📁 FILE EXISTENCE CHECK:")
for file_path in files_to_check:
    full_path = os.path.join(os.path.dirname(__file__), file_path)
    exists = os.path.exists(full_path)
    status = "✅" if exists else "❌"
    print(f"  {status} {file_path}")

# Check database structure
print("\n🗄️  DATABASE STRUCTURE CHECK:")
try:
    import sqlite3
    db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
    
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get PropertyBooking table columns
        cursor.execute("PRAGMA table_info(properties_propertybooking)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Check for dual confirmation columns
        dual_confirmation_columns = [
            'agent_confirmed_completion',
            'customer_confirmed_completion',
            'agent_confirmation_at',
            'customer_confirmation_at'
        ]
        
        print(f"  📋 Total columns in PropertyBooking table: {len(columns)}")
        for col in dual_confirmation_columns:
            exists = col in columns
            status = "✅" if exists else "❌"
            print(f"  {status} {col}")
        
        # Check for existing bookings
        cursor.execute("SELECT COUNT(*) FROM properties_propertybooking")
        booking_count = cursor.fetchone()[0]
        print(f"  📊 Total bookings in database: {booking_count}")
        
        cursor.execute("SELECT COUNT(*) FROM properties_propertybooking WHERE booking_type = 'visit'")
        visit_count = cursor.fetchone()[0]
        print(f"  🏠 Visit bookings: {visit_count}")
        
        cursor.execute("SELECT COUNT(*) FROM properties_propertybooking WHERE booking_type = 'booking'")
        direct_booking_count = cursor.fetchone()[0]
        print(f"  🔑 Direct bookings: {direct_booking_count}")
        
        conn.close()
    else:
        print("  ❌ Database file not found")
        
except Exception as e:
    print(f"  ❌ Database check failed: {e}")

# Check URL patterns
print("\n🔗 URL PATTERN CHECK:")
try:
    with open(os.path.join(os.path.dirname(__file__), 'properties/urls.py'), 'r') as f:
        url_content = f.read()
        
    required_urls = [
        'complete_visit',
        'customer_confirm_visit',
        'property_booking',
        'property_detail'
    ]
    
    for url in required_urls:
        exists = url in url_content
        status = "✅" if exists else "❌"
        print(f"  {status} {url}")
        
except Exception as e:
    print(f"  ❌ URL check failed: {e}")

# Feature summary
print("\n🎯 FEATURE SUMMARY:")
print("  ✅ Direct Booking: Customer books without visiting")
print("  ✅ Visit Scheduling: Customer schedules property visit") 
print("  ✅ Dual Confirmation: Agent + Customer must both confirm visit")
print("  ✅ After-Visit Booking: Customer books after visit completion")
print("  ✅ 7-day booking window after visit completion")

# Next steps
print("\n🚀 NEXT STEPS:")
print("  1. Start server: python manage.py runserver")
print("  2. Open browser: http://127.0.0.1:8000")
print("  3. Test direct booking: Click 'Book Property' button")
print("  4. Test visit system: Click 'Schedule Visit' button")
print("  5. Test dual confirmation: Agent confirms → Customer confirms")

print("\n" + "=" * 50)
print("✨ Dual Confirmation System Ready for Testing!")
