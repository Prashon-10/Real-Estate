import sqlite3
import os

# Check database
db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
print(f"Database path: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check table structure
    cursor.execute("PRAGMA table_info(properties_propertybooking)")
    columns = cursor.fetchall()
    print(f"PropertyBooking columns:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    conn.close()
