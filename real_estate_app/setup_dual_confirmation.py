#!/usr/bin/env python
"""
Simple script to add dual confirmation columns to the database
and test the dual confirmation system.
"""

import sqlite3
import os
import sys

def add_columns():
    db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
    
    if not os.path.exists(db_path):
        print("❌ Database not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get existing columns
        cursor.execute("PRAGMA table_info(properties_propertybooking)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        columns_to_add = [
            ("agent_confirmed_completion", "BOOLEAN DEFAULT 0 NOT NULL"),
            ("customer_confirmed_completion", "BOOLEAN DEFAULT 0 NOT NULL"),
            ("agent_confirmation_at", "DATETIME NULL"),
            ("customer_confirmation_at", "DATETIME NULL")
        ]
        
        added_columns = []
        for col_name, col_def in columns_to_add:
            if col_name not in existing_columns:
                cursor.execute(f"ALTER TABLE properties_propertybooking ADD COLUMN {col_name} {col_def}")
                added_columns.append(col_name)
                print(f"✅ Added column: {col_name}")
            else:
                print(f"⚠️ Column already exists: {col_name}")
        
        conn.commit()
        print(f"\n🎉 Database update completed! Added {len(added_columns)} new columns.")
        
        if added_columns:
            print(f"New columns: {', '.join(added_columns)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    print("🔧 Adding dual confirmation columns to database...")
    success = add_columns()
    
    if success:
        print("\n✨ Dual confirmation system is ready!")
        print("\n📋 System Features:")
        print("  1. Direct Booking: Customers can book without visiting")
        print("  2. Visit Scheduling: Customers can schedule property visits")
        print("  3. Dual Confirmation: Both agent and customer must confirm visit completion")
        print("  4. After-Visit Booking: Customers can book after completing a visit")
        print("\n🚀 You can now start the Django server: python manage.py runserver")
    else:
        print("\n❌ Failed to update database!")
        sys.exit(1)
