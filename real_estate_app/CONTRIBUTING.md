# Contributing to Real Estate Management System

Thank you for considering contributing to our Real Estate Management System! We welcome contributions from everyone.

## 🤝 How to Contribute

### Reporting Bugs
1. **Check existing issues** to avoid duplicates
2. **Create a new issue** with:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Environment details (OS, Python version, Django version)

### Suggesting Features
1. **Check existing feature requests** to avoid duplicates
2. **Create a new issue** with:
   - Clear description of the feature
   - Use case and benefits
   - Mockups or examples if applicable

### Pull Requests
1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Add tests** for new functionality
5. **Update documentation** if needed
6. **Run tests** to ensure everything works
7. **Commit your changes** with clear messages
8. **Push to your branch** (`git push origin feature/amazing-feature`)
9. **Open a Pull Request**

## 📋 Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings for functions and classes
- Keep functions small and focused

### Testing
- Write tests for new features
- Ensure existing tests pass
- Aim for good test coverage

### Documentation
- Update README.md if needed
- Add docstrings to new functions
- Update relevant documentation files

### Git Commit Messages
- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, etc.)
- Keep the first line under 50 characters
- Add details in the body if needed

Example:
```
Add property image upload validation

- Check file size limit (5MB)
- Validate image format (JPG, PNG)
- Add error messages for invalid uploads
```

## 🧪 Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test properties

# Run custom test scripts
python test_admin_improvements.py
python test_dashboard_fixed.py
```

## 🏗️ Development Setup

1. **Clone your fork**
   ```bash
   git clone https://github.com/yourusername/real-estate-management.git
   cd real-estate-management
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up database**
   ```bash
   python manage.py migrate
   python create_sample_data.py
   ```

5. **Run development server**
   ```bash
   python manage.py runserver
   ```

## 📁 Project Structure

Understanding the project structure helps with contributions:

```
real_estate_app/
├── accounts/          # User management
├── core/             # Dashboard and core functionality
├── properties/       # Property management
├── search/          # Search and recommendations
├── templates/       # HTML templates
├── static/         # CSS, JS, images
├── media/          # User uploads
└── docs/           # Documentation
```

## 🎯 Areas for Contribution

We especially welcome contributions in these areas:

### 🐛 Bug Fixes
- Template rendering issues
- Form validation problems
- Database query optimization
- Mobile responsiveness

### ✨ New Features
- Payment integration
- Email notifications
- Advanced search filters
- Property comparison tool
- Map integration
- Calendar scheduling

### 📚 Documentation
- API documentation
- User guides
- Developer tutorials
- Code comments

### 🧪 Testing
- Unit tests
- Integration tests
- UI/UX testing
- Performance testing

## 🚀 Priority Features

Current priority features for contribution:

1. **Payment System Integration**
   - Stripe/PayPal integration
   - Transaction management
   - Payment history

2. **Email Notifications**
   - Property updates
   - New message alerts
   - Weekly summaries

3. **Map Integration**
   - Interactive property maps
   - Location-based search
   - Nearby amenities

4. **Mobile App**
   - React Native app
   - Push notifications
   - Offline capabilities

## 🔍 Code Review Process

1. **Automated checks** must pass
2. **Manual review** by maintainers
3. **Testing** on multiple environments
4. **Documentation** review if applicable
5. **Merge** when approved

## 📞 Getting Help

- 💬 **Discord**: [Join our server](https://discord.gg/yourserver)
- 📧 **Email**: dev@yoursite.com
- 📖 **Wiki**: [Project Wiki](https://github.com/yourusername/real-estate-management/wiki)

## 📜 Code of Conduct

Please note that this project follows our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to abide by its terms.

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project website (if applicable)

Thank you for helping make this project better! 🙏
