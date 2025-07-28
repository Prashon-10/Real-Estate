#!/usr/bin/env python
"""
Script to populate the database with sample data for better admin interface demonstration.
"""

import os
import sys
import django
from pathlib import Path
from decimal import Decimal
import random

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_app.settings')
django.setup()

from django.contrib.auth import get_user_model
from properties.models import Property, PropertyMessage, Favorite
from search.models import SearchHistory, Recommendation

User = get_user_model()

def create_sample_users():
    """Create sample users if they don't exist."""
    sample_users = [
        {
            'username': 'john_agent',
            'email': 'john@realestate.com',
            'first_name': 'John',
            'last_name': 'Smith',
            'user_type': 'agent',
            'is_active': True,
            'email_verified': True,
        },
        {
            'username': 'sarah_agent',
            'email': 'sarah@realestate.com',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'user_type': 'agent',
            'is_active': True,
            'email_verified': True,
        },
        {
            'username': 'mike_customer',
            'email': 'mike@gmail.com',
            'first_name': 'Mike',
            'last_name': 'Davis',
            'user_type': 'customer',
            'is_active': True,
            'email_verified': True,
        },
        {
            'username': 'emma_customer',
            'email': 'emma@yahoo.com',
            'first_name': 'Emma',
            'last_name': 'Wilson',
            'user_type': 'customer',
            'is_active': True,
            'email_verified': True,
        },
        {
            'username': 'alex_customer',
            'email': 'alex@outlook.com',
            'first_name': 'Alex',
            'last_name': 'Brown',
            'user_type': 'customer',
            'is_active': False,
            'email_verified': False,
        }
    ]
    
    created_users = []
    for user_data in sample_users:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults=user_data
        )
        if created:
            user.set_password('password123')
            user.save()
            created_users.append(user)
            print(f"✅ Created user: {user.username}")
        else:
            print(f"📍 User already exists: {user.username}")
    
    return User.objects.filter(username__in=[u['username'] for u in sample_users])

def create_sample_properties():
    """Create sample properties."""
    agents = User.objects.filter(user_type='agent')
    if not agents.exists():
        print("❌ No agents found. Create agents first.")
        return []
    
    sample_properties = [
        {
            'title': 'Beautiful Downtown Apartment',
            'address': '123 Main Street, Downtown, NYC 10001',
            'price': Decimal('750000.00'),
            'bedrooms': 2,
            'bathrooms': Decimal('2.0'),
            'square_footage': 1200,
            'description': 'Stunning 2-bedroom apartment in the heart of downtown with city views, modern amenities, and walking distance to subway.',
            'status': 'available',
        },
        {
            'title': 'Luxury Family Home',
            'address': '456 Oak Avenue, Suburban Heights, NYC 10023',
            'price': Decimal('1250000.00'),
            'bedrooms': 4,
            'bathrooms': Decimal('3.5'),
            'square_footage': 2800,
            'description': 'Spacious family home with large backyard, modern kitchen, and excellent school district.',
            'status': 'available',
        },
        {
            'title': 'Modern Studio Loft',
            'address': '789 Creative District, Brooklyn, NYC 11201',
            'price': Decimal('550000.00'),
            'bedrooms': 1,
            'bathrooms': Decimal('1.0'),
            'square_footage': 800,
            'description': 'Industrial-style loft with high ceilings, exposed brick, and modern finishes in trendy neighborhood.',
            'status': 'pending',
        },
        {
            'title': 'Cozy Garden Apartment',
            'address': '321 Garden Lane, Queens, NYC 11375',
            'price': Decimal('480000.00'),
            'bedrooms': 1,
            'bathrooms': Decimal('1.0'),
            'square_footage': 650,
            'description': 'Charming ground-floor apartment with private garden access and updated kitchen.',
            'status': 'sold',
        },
        {
            'title': 'Penthouse with Terrace',
            'address': '555 Sky Tower, Manhattan, NYC 10014',
            'price': Decimal('2500000.00'),
            'bedrooms': 3,
            'bathrooms': Decimal('2.5'),
            'square_footage': 1800,
            'description': 'Exclusive penthouse with wraparound terrace, panoramic city views, and luxury finishes throughout.',
            'status': 'available',
        }
    ]
    
    created_properties = []
    for i, prop_data in enumerate(sample_properties):
        prop_data['agent'] = agents[i % len(agents)]
        
        # Check if property already exists
        existing = Property.objects.filter(
            title=prop_data['title']
        ).first()
        
        if not existing:
            property_obj = Property.objects.create(**prop_data)
            created_properties.append(property_obj)
            print(f"✅ Created property: {property_obj.title}")
        else:
            created_properties.append(existing)
            print(f"📍 Property already exists: {existing.title}")
    
    return created_properties

def create_sample_messages():
    """Create sample property messages."""
    properties = Property.objects.all()
    customers = User.objects.filter(user_type='customer')
    
    if not properties.exists() or not customers.exists():
        print("❌ Need properties and customers to create messages.")
        return
    
    sample_messages = [
        "I'm very interested in this property. Can we schedule a viewing?",
        "Is this property still available? I'd like more information about the neighborhood.",
        "What's the earliest move-in date? I'm looking to relocate soon.",
        "Are pets allowed in this property? I have a small dog.",
        "Can you provide more details about the parking situation?",
        "I love the photos! When would be a good time for a tour?",
        "Is there any room for negotiation on the price?",
        "What are the monthly maintenance fees?",
    ]
    
    created_count = 0
    for property_obj in properties[:3]:  # Create messages for first 3 properties
        for i in range(random.randint(1, 3)):  # 1-3 messages per property
            customer = random.choice(customers)
            message = random.choice(sample_messages)
            
            property_message = PropertyMessage.objects.create(
                property=property_obj,
                sender=customer,
                content=message,
                read=random.choice([True, False])
            )
            created_count += 1
    
    print(f"✅ Created {created_count} property messages")

def create_sample_favorites():
    """Create sample favorites."""
    properties = Property.objects.all()
    customers = User.objects.filter(user_type='customer')
    
    if not properties.exists() or not customers.exists():
        print("❌ Need properties and customers to create favorites.")
        return
    
    created_count = 0
    for customer in customers:
        # Each customer favorites 1-3 properties
        property_count = min(random.randint(1, 3), properties.count())
        favorite_properties = random.sample(list(properties), property_count)
        
        for property_obj in favorite_properties:
            favorite, created = Favorite.objects.get_or_create(
                user=customer,
                property=property_obj
            )
            if created:
                created_count += 1
    
    print(f"✅ Created {created_count} favorites")

def create_sample_search_history():
    """Create sample search history."""
    customers = User.objects.filter(user_type='customer')
    properties = Property.objects.all()
    
    if not customers.exists():
        print("❌ Need customers to create search history.")
        return
    
    sample_queries = [
        "2 bedroom apartment downtown",
        "luxury family home",
        "studio apartment under 600k",
        "penthouse with terrace",
        "pet-friendly apartment",
        "modern loft brooklyn",
        "apartment with garden",
        "3 bedroom house",
    ]
    
    created_count = 0
    for customer in customers:
        # Each customer has 2-5 searches
        search_count = random.randint(2, 5)
        for _ in range(search_count):
            query = random.choice(sample_queries)
            property_obj = random.choice(properties) if properties.exists() and random.choice([True, False]) else None
            
            SearchHistory.objects.create(
                user=customer,
                query=query,
                property=property_obj
            )
            created_count += 1
    
    print(f"✅ Created {created_count} search history entries")

def create_sample_recommendations():
    """Create sample recommendations."""
    customers = User.objects.filter(user_type='customer')
    properties = Property.objects.all()
    
    if not customers.exists() or not properties.exists():
        print("❌ Need customers and properties to create recommendations.")
        return
    
    created_count = 0
    for customer in customers:
        # Each customer gets 2-4 recommendations
        rec_count = min(random.randint(2, 4), properties.count())
        recommended_properties = random.sample(list(properties), rec_count)
        
        for property_obj in recommended_properties:
            score = round(random.uniform(6.0, 9.5), 1)
            
            recommendation, created = Recommendation.objects.get_or_create(
                user=customer,
                property=property_obj,
                defaults={'score': score}
            )
            if created:
                created_count += 1
    
    print(f"✅ Created {created_count} recommendations")

def main():
    """Main function to create all sample data."""
    print("🏠 CREATING SAMPLE DATA FOR REALESTATE ADMIN")
    print("=" * 50)
    
    try:
        # Create sample data
        print("\n1. Creating sample users...")
        users = create_sample_users()
        
        print("\n2. Creating sample properties...")
        properties = create_sample_properties()
        
        print("\n3. Creating sample messages...")
        create_sample_messages()
        
        print("\n4. Creating sample favorites...")
        create_sample_favorites()
        
        print("\n5. Creating sample search history...")
        create_sample_search_history()
        
        print("\n6. Creating sample recommendations...")
        create_sample_recommendations()
        
        print("\n" + "=" * 50)
        print("✅ SAMPLE DATA CREATION COMPLETED!")
        print("\n📊 Summary:")
        print(f"   Users: {User.objects.count()}")
        print(f"   Properties: {Property.objects.count()}")
        print(f"   Messages: {PropertyMessage.objects.count()}")
        print(f"   Favorites: {Favorite.objects.count()}")
        print(f"   Search History: {SearchHistory.objects.count()}")
        print(f"   Recommendations: {Recommendation.objects.count()}")
        
        print("\n🔗 Access admin at: http://127.0.0.1:8000/admin/")
        print("   Username: admin")
        print("   Password: (the one you created)")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error creating sample data: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
