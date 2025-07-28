# Real Estate Application Documentation

## Overview
A comprehensive Django-based real estate platform with AI-powered search capabilities, real-time messaging, and role-based user management.

## Architecture
- **Framework**: Django 5.2.1
- **Database**: SQLite (Development), supports PostgreSQL/MySQL for production
- **AI/ML**: Sentence Transformers for semantic search
- **Real-time**: Django Channels with Redis
- **Frontend**: Bootstrap 5.3.0 with custom CSS

## Documentation Structure

### Diagrams
- [Entity Relationship Diagram](er_diagram.puml) - Database schema and relationships
- [Class Diagram](class_diagram.puml) - Object-oriented structure
- [Object Instance Diagram](object_instance_diagram.puml) - Sample data instances
- [System Architecture](system_architecture.puml) - High-level system design
- [Component Diagram](component_diagram.puml) - Internal application structure
- [Deployment Diagram](deployment_diagram.puml) - Production deployment architecture
- [Data Flow Diagrams](dataflow/) - Process flows at different levels
- [Sequence Diagrams](sequence/) - User interaction flows
- [Use Case Diagram](use_case_diagram.puml) - User stories and system interactions
- [Property State Diagram](property_state_diagram.puml) - Property lifecycle states
- [User Journey State Diagram](user_journey_state_diagram.puml) - User interaction states

### Technical Documentation
- [API Documentation](api.md) - REST endpoints and WebSocket APIs
- [Database Schema](database.md) - Detailed table structures
- [Deployment Guide](deployment.md) - Production deployment instructions
- [Development Setup](development.md) - Local development environment
- [Testing Guide](testing.md) - Testing strategies and procedures

### User Guides
- [User Manual](user_guide.md) - End-user documentation
- [Admin Guide](admin_guide.md) - Administrative functions
- [Agent Guide](agent_guide.md) - Property agent workflows

## Quick Start
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Create superuser: `python manage.py createsuperuser`
5. Start development server: `python manage.py runserver`

## Features
- **User Management**: Multi-role authentication (Customer, Agent, Admin)
- **Property Management**: CRUD operations with image uploads
- **AI Search**: Semantic search using natural language processing
- **Recommendations**: Personalized property suggestions
- **Messaging**: Real-time communication between users and agents
- **Favorites**: Property bookmarking system
- **Advanced Filtering**: Multi-criteria property search

## Technology Stack
- Python 3.12+
- Django 5.2.1
- Django Channels for WebSockets
- Sentence Transformers for AI
- Bootstrap 5 for UI
- Redis for caching and channels
- SQLite/PostgreSQL for data storage
