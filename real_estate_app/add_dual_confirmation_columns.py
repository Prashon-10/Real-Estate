#!/usr/bin/env python
import os
import sys
import sqlite3

def add_dual_confirmation_columns():
    """Add dual confirmation columns to PropertyBooking table"""
    # Path to the SQLite database
    db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found at {db_path}")
        return
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get existing columns
        cursor.execute("PRAGMA table_info(properties_propertybooking)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Existing columns: {columns}")
        
        # Add columns if they don't exist
        if 'agent_confirmed_completion' not in columns:
            cursor.execute("""
                ALTER TABLE properties_propertybooking 
                ADD COLUMN agent_confirmed_completion BOOLEAN DEFAULT 0 NOT NULL
            """)
            print("✅ Added agent_confirmed_completion column")
        else:
            print("⚠️ agent_confirmed_completion column already exists")
        
        if 'customer_confirmed_completion' not in columns:
            cursor.execute("""
                ALTER TABLE properties_propertybooking 
                ADD COLUMN customer_confirmed_completion BOOLEAN DEFAULT 0 NOT NULL
            """)
            print("✅ Added customer_confirmed_completion column")
        else:
            print("⚠️ customer_confirmed_completion column already exists")
        
        if 'agent_confirmation_at' not in columns:
            cursor.execute("""
                ALTER TABLE properties_propertybooking 
                ADD COLUMN agent_confirmation_at DATETIME NULL
            """)
            print("✅ Added agent_confirmation_at column")
        else:
            print("⚠️ agent_confirmation_at column already exists")
        
        if 'customer_confirmation_at' not in columns:
            cursor.execute("""
                ALTER TABLE properties_propertybooking 
                ADD COLUMN customer_confirmation_at DATETIME NULL
            """)
            print("✅ Added customer_confirmation_at column")
        else:
            print("⚠️ customer_confirmation_at column already exists")
        
        # Commit changes
        conn.commit()
        print("🎉 Database updated successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    add_dual_confirmation_columns()
