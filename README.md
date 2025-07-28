# 🏠 Real Estate Management System

A comprehensive Django-based real estate management platform that connects property agents with potential customers, featuring property listings, user management, search functionality, and administrative tools.

## 🌟 Features

### 👥 User Management
- **Multi-type User System**: Support for Customers, Agents, and Admins
- **Profile Management**: Custom user profiles with images and contact information
- **Authentication System**: Secure login/logout with user type-based permissions

### 🏘️ Property Management
- **Property Listings**: Create, edit, and manage property listings
- **Image Gallery**: Multiple images per property with preview functionality
- **Property Status**: Available, Pending, Sold status tracking
- **Advanced Filters**: Search by location, price, bedrooms, bathrooms, etc.

### 🔍 Search & Discovery
- **Advanced Search**: Filter properties by multiple criteria
- **Recommendations**: Personalized property recommendations for users
- **Search History**: Track and display user search patterns
- **Favorites System**: Save and manage favorite properties

### 💬 Communication
- **Messaging System**: Direct communication between agents and customers
- **Property Inquiries**: Structured inquiry system for property details
- **Message Management**: Read/unread status and organized conversations

### 📊 Dashboard & Analytics
- **User Dashboard**: Personalized dashboards for different user types
- **Agent Tools**: Property management, customer interactions, performance metrics
- **Admin Panel**: Comprehensive admin interface with custom statistics
- **Real-time Statistics**: Live data on users, properties, and activities

### 🎨 UI/UX Features
- **Responsive Design**: Mobile-friendly interface
- **Modern Styling**: Bootstrap-based professional design
- **Interactive Elements**: Smooth animations and transitions
- **Draggable Admin Filters**: Customizable admin interface
- **Professional Themes**: Consistent branding throughout

## 🛠️ Technology Stack

- **Backend**: Django 5.2.3 (Python)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5.3
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Icons**: Font Awesome 6.4
- **Fonts**: Google Fonts (Inter)

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/real-estate-management.git
   cd real-estate-management
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Load sample data (optional)**
   ```bash
   python create_sample_data.py
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

8. **Visit the application**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/
   - Dashboard: http://127.0.0.1:8000/dashboard/

## 🗂️ Project Structure

```
real_estate_app/
├── accounts/           # User management app
├── core/              # Core functionality and dashboard
├── properties/        # Property management app
├── search/           # Search and recommendations
├── templates/        # HTML templates
├── static/          # Static files (CSS, JS, images)
├── media/           # User uploaded files
├── docs/            # Documentation
├── manage.py        # Django management script
└── requirements.txt # Python dependencies
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Media Files
The application handles user-uploaded content:
- Profile images: `media/profile_images/`
- Property images: `media/property_images/`

## 👤 User Types & Permissions

### 🛒 Customer
- Browse and search properties
- Save favorite properties
- Contact agents
- View recommendations
- Manage profile

### 🏢 Agent
- Create and manage property listings
- Communicate with customers
- View property analytics
- Manage client interactions

### ⚙️ Admin
- Full system access
- User management
- Property oversight
- System statistics
- Content moderation

## 📱 Key Pages

- **Home**: Property showcase and search
- **Property Listings**: Browse all available properties
- **Property Detail**: Detailed property information
- **Dashboard**: User-specific control panel
- **Profile**: User account management
- **Admin**: System administration interface

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

Custom test scripts are available:
```bash
python test_admin_improvements.py
python test_dashboard_fixed.py
```

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:
- API Documentation
- Database Schema
- Development Guide
- Deployment Instructions
- User Guide

## 🚀 Deployment

### Production Setup
1. Set `DEBUG=False` in settings
2. Configure production database (PostgreSQL recommended)
3. Set up static files serving
4. Configure email backend
5. Set up HTTPS
6. Configure allowed hosts

### Environment Variables for Production
```env
SECRET_KEY=your-production-secret-key
DEBUG=False
DATABASE_URL=postgresql://user:password@localhost/dbname
EMAIL_HOST=smtp.your-email-provider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Demo**: [Live Demo](https://your-demo-site.com)
- **Documentation**: [Full Docs](https://your-docs-site.com)
- **Issues**: [GitHub Issues](https://github.com/yourusername/real-estate-management/issues)

## 📞 Support

For support and questions:
- 📧 Email: support@yoursite.com
- 💬 Discord: [Join our server](https://discord.gg/yourserver)
- 📖 Wiki: [Project Wiki](https://github.com/yourusername/real-estate-management/wiki)

## 🏆 Acknowledgments

- Django framework and community
- Bootstrap for responsive design
- Font Awesome for icons
- All contributors and testers

---

**Built with ❤️ using Django**
