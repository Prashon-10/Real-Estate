# Real Estate Management System

A Django-based real estate management application for property listings, user management, and property search functionality.

## Features

- **User Management**: Registration, login, profile management
- **Property Management**: Add, edit, delete property listings
- **Search Functionality**: Advanced property search with filters
- **Admin Panel**: Custom admin interface for property management
- **Chat System**: Communication between users
- **Booking System**: Property booking functionality
- **Media Management**: Image uploads for properties and profiles

## Project Structure

```
real_estate_app/
├── accounts/           # User authentication and profile management
├── admin_panel/        # Custom admin interface
├── chat/              # Chat functionality
├── core/              # Core application logic
├── properties/        # Property listings and booking
├── search/            # Search functionality
├── templates/         # HTML templates
├── media/             # User uploaded files
├── real_estate_app/   # Main Django project settings
├── manage.py          # Django management script
├── requirements.txt   # Python dependencies
└── start_server.bat   # Server startup script
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run migrations:
   ```bash
   python manage.py migrate
   ```
4. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
5. Start the development server:
   ```bash
   python manage.py runserver
   ```
   Or use the provided batch file:
   ```bash
   start_server.bat
   ```

## Access URLs

- **Main Application**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin-panel/
- **Django Admin**: http://127.0.0.1:8000/admin/

## Default Admin Credentials

- Username: admin
- Password: admin123

## Technologies Used

- **Backend**: Django 5.2.1
- **Database**: SQLite (default)
- **Frontend**: HTML, CSS, JavaScript
- **Real-time Features**: Django Channels with Redis
- **AI/ML**: Sentence Transformers for search functionality
- **Image Processing**: Pillow

## License

MIT License - see LICENSE file for details
