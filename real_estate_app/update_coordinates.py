#!/usr/bin/env python
"""
Quick script to add sample coordinates to existing properties for testing
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_app.settings')
django.setup()

from properties.models import Property

# Sample coordinates for different areas in Nepal (Kathmandu valley)
sample_coordinates = [
    (27.7172, 85.3240),  # Kathmandu center
    (27.6710, 85.4298),  # Bhaktapur
    (27.6737, 85.3154),  # Lalitpur/Patan
    (27.7485, 85.3575),  # Budhanilkantha
    (27.6965, 85.3438),  # Thamel
    (27.7103, 85.3222),  # New Baneshwor
    (27.6892, 85.3448),  # Durbarmarg
    (27.7145, 85.3560),  # Maharajgunj
    (27.6643, 85.3188),  # Jawalakhel
    (27.7256, 85.3370),  # Baluwatar
]

def update_property_coordinates():
    """Update properties with sample coordinates"""
    properties = Property.objects.filter(latitude__isnull=True, longitude__isnull=True)
    
    print(f"Found {properties.count()} properties without coordinates")
    
    updated_count = 0
    for i, property_obj in enumerate(properties):
        if i < len(sample_coordinates):
            lat, lng = sample_coordinates[i]
            property_obj.latitude = lat
            property_obj.longitude = lng
            property_obj.save()
            print(f"Updated {property_obj.title} with coordinates ({lat}, {lng})")
            updated_count += 1
    
    print(f"\nUpdated {updated_count} properties with coordinates")
    
    # Show all properties with coordinates
    all_properties = Property.objects.exclude(latitude__isnull=True, longitude__isnull=True)
    print(f"\nProperties with coordinates ({all_properties.count()} total):")
    for prop in all_properties[:5]:  # Show first 5
        print(f"- {prop.title}: ({prop.latitude}, {prop.longitude})")

if __name__ == "__main__":
    update_property_coordinates()
