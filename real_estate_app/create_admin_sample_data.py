#!/usr/bin/env python
"""
Create sample data for testing admin interface
"""
import os
import sys
import django
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_app.settings')
django.setup()

from properties.models import Property, Favorite, PropertyImage, PropertyMessage
from search.models import SearchHistory, Recommendation

User = get_user_model()

def create_sample_admin_data():
    """Create sample data for admin testing"""
    print("🏗️  Creating sample data for admin interface...")
    
    # Create users if they don't exist
    try:
        admin_user = User.objects.get(username='admin')
        print("✅ Admin user already exists")
    except User.DoesNotExist:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@realestate.com',
            password='admin123',
            user_type='admin'
        )
        print("✅ Created admin user")
    
    # Create agents
    agents = []
    for i in range(3):
        try:
            agent = User.objects.get(username=f'agent{i+1}')
            agents.append(agent)
        except User.DoesNotExist:
            agent = User.objects.create_user(
                username=f'agent{i+1}',
                email=f'agent{i+1}@realestate.com',
                password='agent123',
                user_type='agent',
                first_name=f'Agent {i+1}',
                last_name='Smith'
            )
            agents.append(agent)
    print(f"✅ Created {len(agents)} agents")
    
    # Create customers
    customers = []
    for i in range(5):
        try:
            customer = User.objects.get(username=f'customer{i+1}')
            customers.append(customer)
        except User.DoesNotExist:
            customer = User.objects.create_user(
                username=f'customer{i+1}',
                email=f'customer{i+1}@email.com',
                password='customer123',
                user_type='customer',
                first_name=f'Customer {i+1}',
                last_name='Johnson'
            )
            customers.append(customer)
    print(f"✅ Created {len(customers)} customers")
    
    # Create properties
    property_data = [
        {
            'title': 'Modern Downtown Apartment',
            'address': '123 Main St, Downtown, City',
            'price': 250000.00,
            'bedrooms': 2,
            'bathrooms': 2,
            'square_footage': 1200,
            'description': 'Beautiful modern apartment in the heart of downtown.',
            'status': 'available'
        },
        {
            'title': 'Suburban Family Home',
            'address': '456 Oak Ave, Suburbia, City',
            'price': 450000.00,
            'bedrooms': 4,
            'bathrooms': 3,
            'square_footage': 2500,
            'description': 'Spacious family home with large backyard.',
            'status': 'available'
        },
        {
            'title': 'Luxury Penthouse',
            'address': '789 Sky Tower, Uptown, City',
            'price': 850000.00,
            'bedrooms': 3,
            'bathrooms': 3,
            'square_footage': 2000,
            'description': 'Luxury penthouse with stunning city views.',
            'status': 'pending'
        },
        {
            'title': 'Cozy Studio Loft',
            'address': '321 Art District, Creative Quarter, City',
            'price': 180000.00,
            'bedrooms': 1,
            'bathrooms': 1,
            'square_footage': 800,
            'description': 'Artistic loft in the creative quarter.',
            'status': 'sold'
        },
        {
            'title': 'Waterfront Condo',
            'address': '555 Beach Blvd, Waterfront, City',
            'price': 380000.00,
            'bedrooms': 2,
            'bathrooms': 2,
            'square_footage': 1400,
            'description': 'Beautiful waterfront condo with ocean views.',
            'status': 'available'
        }
    ]
    
    properties = []
    for i, prop_data in enumerate(property_data):
        try:
            prop = Property.objects.get(title=prop_data['title'])
            properties.append(prop)
        except Property.DoesNotExist:
            prop = Property.objects.create(
                agent=agents[i % len(agents)],
                **prop_data
            )
            properties.append(prop)
    print(f"✅ Created {len(properties)} properties")
    
    # Create favorites
    favorites_created = 0
    for customer in customers[:3]:
        for prop in properties[:2]:
            favorite, created = Favorite.objects.get_or_create(
                user=customer,
                property=prop
            )
            if created:
                favorites_created += 1
    print(f"✅ Created {favorites_created} favorites")
    
    # Create property messages
    messages_created = 0
    for i, customer in enumerate(customers[:3]):
        for prop in properties[:2]:
            message, created = PropertyMessage.objects.get_or_create(
                property=prop,
                sender=customer,
                defaults={
                    'content': f'Hi, I\'m interested in this property. Could you provide more information about {prop.title}?',
                    'read': i % 2 == 0  # Some read, some unread
                }
            )
            if created:
                messages_created += 1
    print(f"✅ Created {messages_created} property messages")
    
    # Create search history
    search_queries = [
        'downtown apartment',
        'family home suburban',
        'luxury penthouse',
        'waterfront condo',
        'studio loft'
    ]
    
    searches_created = 0
    for i, customer in enumerate(customers):
        for j, query in enumerate(search_queries[:3]):
            search, created = SearchHistory.objects.get_or_create(
                user=customer,
                query=query,
                property=properties[j % len(properties)]
            )
            if created:
                searches_created += 1
    print(f"✅ Created {searches_created} search history entries")
    
    # Create recommendations
    recommendations_created = 0
    for customer in customers[:3]:
        for prop in properties[:2]:
            recommendation, created = Recommendation.objects.get_or_create(
                user=customer,
                property=prop,
                defaults={
                    'score': 8.5 + (0.5 * (hash(customer.username + prop.title) % 3))
                }
            )
            if created:
                recommendations_created += 1
    print(f"✅ Created {recommendations_created} recommendations")
    
    print("\n🎉 Sample data creation completed!")
    print("📊 Summary:")
    print(f"   • Users: {User.objects.count()}")
    print(f"   • Properties: {Property.objects.count()}")
    print(f"   • Favorites: {Favorite.objects.count()}")
    print(f"   • Messages: {PropertyMessage.objects.count()}")
    print(f"   • Search History: {SearchHistory.objects.count()}")
    print(f"   • Recommendations: {Recommendation.objects.count()}")
    print("\n🔑 Admin Login: username='admin', password='admin123'")

if __name__ == '__main__':
    create_sample_admin_data()
