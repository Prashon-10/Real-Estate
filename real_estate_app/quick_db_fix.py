import sqlite3
import os

# Direct database manipulation
db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')

print(f"Database path: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(properties_propertybooking)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Existing columns: {len(columns)} columns found")
    
    # Add columns if they don't exist
    columns_to_add = [
        "agent_confirmed_completion",
        "customer_confirmed_completion", 
        "agent_confirmation_at",
        "customer_confirmation_at"
    ]
    
    for col in columns_to_add:
        if col not in columns:
            if 'confirmation_at' in col:
                cursor.execute(f"ALTER TABLE properties_propertybooking ADD COLUMN {col} DATETIME NULL")
            else:
                cursor.execute(f"ALTER TABLE properties_propertybooking ADD COLUMN {col} BOOLEAN DEFAULT 0 NOT NULL")
            print(f"Added column: {col}")
        else:
            print(f"Column exists: {col}")
    
    conn.commit()
    conn.close()
    print("Database update completed!")
else:
    print("Database not found!")
