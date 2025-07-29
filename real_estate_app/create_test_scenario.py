#!/usr/bin/env python
"""
Final comprehensive test of the agent message system
This creates a realistic scenario and provides step-by-step instructions
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_app.settings')
django.setup()

from accounts.models import User
from properties.models import Property, PropertyMessage
from django.contrib.auth.hashers import make_password

def create_realistic_test_scenario():
    print("🏠 Creating Realistic Agent Message Test Scenario")
    print("=" * 60)
    
    # Create a realistic agent
    agent, created = User.objects.get_or_create(
        username='raja_agent',
        defaults={
            'email': 'raja@realestate.com',
            'password': make_password('agent123'),
            'user_type': 'agent',
            'first_name': 'Raja',
            'last_name': 'Ram',
            'phone_number': '987455568'
        }
    )
    print(f"✅ Agent: {agent.first_name} {agent.last_name} ({'Created' if created else 'Found'})")
    
    # Create realistic customers
    customers_data = [
        {'username': 'nitesh_customer', 'first_name': 'Nitesh', 'last_name': 'Adhikari', 'email': 'nitesh1@gmail.com'},
        {'username': 'priya_customer', 'first_name': 'Priya', 'last_name': 'Sharma', 'email': 'priya@gmail.com'},
        {'username': 'amit_customer', 'first_name': 'Amit', 'last_name': 'Patel', 'email': 'amit@gmail.com'},
    ]
    
    customers = []
    for customer_data in customers_data:
        customer, created = User.objects.get_or_create(
            username=customer_data['username'],
            defaults={
                'email': customer_data['email'],
                'password': make_password('customer123'),
                'user_type': 'customer',
                'first_name': customer_data['first_name'],
                'last_name': customer_data['last_name']
            }
        )
        customers.append(customer)
        print(f"✅ Customer: {customer.first_name} {customer.last_name} ({'Created' if created else 'Found'})")
    
    # Create realistic properties
    properties_data = [
        {
            'title': 'Modern Family Home with Garden View',
            'address': '123 Green Valley Road, Kathmandu',
            'price': 450000,
            'bedrooms': 4,
            'bathrooms': 3,
            'square_footage': 2200,
            'description': 'Beautiful modern family home with garden view and spacious rooms.'
        },
        {
            'title': 'Luxury Apartment Downtown',
            'address': '456 City Center, Lalitpur',
            'price': 350000,
            'bedrooms': 2,
            'bathrooms': 2,
            'square_footage': 1200,
            'description': 'Luxury apartment in the heart of the city with all amenities.'
        }
    ]
    
    properties = []
    for prop_data in properties_data:
        property_obj, created = Property.objects.get_or_create(
            title=prop_data['title'],
            defaults={
                **prop_data,
                'agent': agent,
                'listing_type': 'sale',
                'property_type': 'house',
                'status': 'available'
            }
        )
        properties.append(property_obj)
        print(f"✅ Property: {property_obj.title} ({'Created' if created else 'Found'})")
    
    # Create realistic messages
    messages_data = [
        {
            'customer': customers[0],  # Nitesh
            'property': properties[0],  # Modern Family Home
            'content': "Hi Raja Ram! I'm interested in the property 'Modern Family Home with Garden View'. Could you please provide more information about it? I'd love to schedule a viewing at your convenience."
        },
        {
            'customer': customers[1],  # Priya
            'property': properties[0],  # Modern Family Home
            'content': "Hello! I saw your listing for the Modern Family Home. Is this property still available? What's the neighborhood like?"
        },
        {
            'customer': customers[2],  # Amit
            'property': properties[1],  # Luxury Apartment
            'content': "Hi, I'm very interested in the Luxury Apartment Downtown. Can we arrange a viewing this weekend? Also, what are the maintenance charges?"
        },
        {
            'customer': customers[0],  # Nitesh again
            'property': properties[1],  # Luxury Apartment
            'content': "Hi Raja! Apart from the family home, I'm also considering your luxury apartment. Could you send me more details about the apartment features?"
        }
    ]
    
    # Clear existing messages for this agent to start fresh
    existing_messages = PropertyMessage.objects.filter(property__agent=agent)
    print(f"\n🧹 Clearing {existing_messages.count()} existing messages for fresh test...")
    existing_messages.delete()
    
    # Create new messages
    print(f"\n📨 Creating new customer messages...")
    for i, msg_data in enumerate(messages_data, 1):
        message = PropertyMessage.objects.create(
            property=msg_data['property'],
            sender=msg_data['customer'],
            content=msg_data['content']
        )
        print(f"   {i}. From {msg_data['customer'].first_name}: {msg_data['content'][:60]}...")
    
    # Final status
    print(f"\n📊 Final Status:")
    agent_messages = PropertyMessage.objects.filter(property__agent=agent)
    unread_messages = agent_messages.filter(read=False)
    
    print(f"   Agent: {agent.first_name} {agent.last_name} ({agent.username})")
    print(f"   Total properties: {Property.objects.filter(agent=agent).count()}")
    print(f"   Total messages: {agent_messages.count()}")
    print(f"   Unread messages: {unread_messages.count()}")
    
    print(f"\n🎯 Test Instructions:")
    print(f"1. Open browser and go to: http://127.0.0.1:8000/accounts/login/")
    print(f"2. Login as agent:")
    print(f"   Username: {agent.username}")
    print(f"   Password: agent123")
    print(f"3. After login, you should see:")
    print(f"   - Dashboard with {unread_messages.count()} unread messages")
    print(f"   - 'Messages' button in Quick Actions")
    print(f"   - Messages link in navigation (if enabled)")
    print(f"4. Click 'Messages' to go to: http://127.0.0.1:8000/properties/messages/")
    print(f"5. You should see {agent_messages.count()} messages from customers")
    print(f"6. All messages should be marked as 'Unread' initially")
    print(f"7. Click 'Mark as Read' on any message to test functionality")
    
    print(f"\n📋 Expected Messages in Inbox:")
    for i, message in enumerate(agent_messages.order_by('-timestamp'), 1):
        print(f"   {i}. From: {message.sender.first_name} {message.sender.last_name}")
        print(f"      Property: {message.property.title}")
        print(f"      Content: {message.content[:100]}...")
        print(f"      Status: {'Unread' if not message.read else 'Read'}")
        print("")
    
    print(f"✅ Test scenario created successfully!")
    print(f"🔗 Direct links:")
    print(f"   Login: http://127.0.0.1:8000/accounts/login/")
    print(f"   Dashboard: http://127.0.0.1:8000/dashboard/")
    print(f"   Messages: http://127.0.0.1:8000/properties/messages/")

if __name__ == '__main__':
    create_realistic_test_scenario()
