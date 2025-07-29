#!/usr/bin/env python
import os
import sys
import django

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_app.settings')
django.setup()

from properties.models import Property
import random

def update_properties():
    """Update existing properties with random listing types and property types"""
    
    listing_types = ['sale', 'rent']
    property_types = ['house', 'apartment', 'condo', 'villa']
    
    properties = Property.objects.all()
    
    for i, property in enumerate(properties):
        # Assign listing type based on price (higher prices are more likely to be sales)
        if property.price > 50000000:  # 5 crore+
            property.listing_type = 'sale'
        elif property.price < 10000000:  # Less than 1 crore
            property.listing_type = random.choice(['rent', 'sale'])
        else:
            property.listing_type = random.choice(listing_types)
        
        # Assign property type based on title keywords
        title_lower = property.title.lower()
        if 'apartment' in title_lower or 'flat' in title_lower:
            property.property_type = 'apartment'
        elif 'villa' in title_lower:
            property.property_type = 'villa'
        elif 'condo' in title_lower:
            property.property_type = 'condo'
        elif 'house' in title_lower or 'home' in title_lower:
            property.property_type = 'house'
        else:
            property.property_type = random.choice(property_types)
        
        # Make some properties featured
        property.is_featured = (i % 4 == 0)  # Every 4th property is featured
        
        property.save()
        print(f"Updated {property.title}: {property.listing_type}, {property.property_type}, Featured: {property.is_featured}")

if __name__ == "__main__":
    update_properties()
    print("Properties updated successfully!")
