# Development Setup Guide

## Prerequisites

### System Requirements
- **Python**: 3.12 or higher
- **Node.js**: 18+ (for frontend build tools)
- **Redis**: 6.0+ (for channels and caching)
- **Git**: Latest version

### Development Tools
- **Code Editor**: VS Code (recommended) or PyCharm
- **Database Client**: DB Browser for SQLite or pgAdmin
- **API Testing**: Postman or Insomnia
- **Version Control**: Git with GitHub/GitLab

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/your-org/real-estate-app.git
cd real-estate-app
```

### 2. Virtual Environment Setup
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### 4. Environment Configuration
Create `.env` file in project root:
```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3
# For PostgreSQL: postgresql://user:password@localhost:5432/realestate_db

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
CHANNEL_LAYERS_BACKEND=channels_redis.core.RedisChannelLayer

# Email Settings (Development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=localhost
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# Media and Static Files
MEDIA_ROOT=media/
STATIC_ROOT=staticfiles/

# AI/ML Settings
SENTENCE_TRANSFORMERS_MODEL=all-MiniLM-L6-v2
RECOMMENDATION_THRESHOLD=0.2
MAX_RECOMMENDATIONS=50

# Logging
LOG_LEVEL=DEBUG
LOG_FILE=logs/django.log
```

### 5. Database Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata fixtures/sample_data.json
```

### 6. Static Files
```bash
# Collect static files
python manage.py collectstatic --noinput

# Install frontend dependencies (if applicable)
npm install

# Build frontend assets
npm run build
```

### 7. Redis Setup
```bash
# Install Redis (Ubuntu/Debian)
sudo apt update
sudo apt install redis-server

# Start Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis connection
redis-cli ping
# Should return: PONG
```

### 8. AI Model Download
```bash
# Download Sentence Transformers model
python manage.py shell
>>> from sentence_transformers import SentenceTransformer
>>> model = SentenceTransformer('all-MiniLM-L6-v2')
>>> exit()
```

## Development Server

### Start Development Environment
```bash
# Terminal 1: Start Django development server
python manage.py runserver

# Terminal 2: Start Redis (if not running as service)
redis-server

# Terminal 3: Start Celery worker (if using background tasks)
celery -A real_estate_app worker --loglevel=info

# Terminal 4: Start Celery beat (for scheduled tasks)
celery -A real_estate_app beat --loglevel=info
```

### Access Points
- **Web Application**: http://localhost:8000
- **Admin Interface**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/api/docs/
- **Redis CLI**: `redis-cli` in terminal

## Development Workflow

### Code Quality Tools

#### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

#### Linting and Formatting
```bash
# Black code formatter
black .

# isort import sorting
isort .

# flake8 linting
flake8 .

# mypy type checking
mypy .

# pylint code analysis
pylint real_estate_app/
```

#### Testing
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test properties

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html

# Run tests with pytest (alternative)
pytest
pytest --cov=. --cov-report=html
```

### Database Management

#### Migrations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Rollback migration
python manage.py migrate app_name 0001
```

#### Data Management
```bash
# Create fixture from existing data
python manage.py dumpdata app_name > fixtures/app_data.json

# Load fixture data
python manage.py loaddata fixtures/app_data.json

# Reset database (careful!)
python manage.py flush
```

### Debugging

#### Django Debug Toolbar
Add to `INSTALLED_APPS` in development:
```python
INSTALLED_APPS = [
    # ... other apps
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # ... other middleware
]
```

#### Logging Configuration
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'real_estate_app': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

## IDE Configuration

### VS Code Settings
Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "files.associations": {
        "*.html": "html"
    },
    "emmet.includeLanguages": {
        "django-html": "html"
    }
}
```

### Recommended Extensions
- Python
- Django
- HTML CSS Support
- Auto Rename Tag
- GitLens
- Thunder Client (API testing)

## Common Issues & Solutions

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>
```

### Database Locked Error
```bash
# Stop all Django processes
# Delete db.sqlite3 (if safe to do so)
# Run migrations again
python manage.py migrate
```

### Redis Connection Error
```bash
# Check Redis status
sudo systemctl status redis-server

# Restart Redis
sudo systemctl restart redis-server

# Check Redis logs
sudo journalctl -u redis-server
```

### Model Import Error
```bash
# Download models manually
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Static Files Not Loading
```bash
# Ensure DEBUG=True in development
# Check STATIC_URL and STATICFILES_DIRS
# Run collectstatic
python manage.py collectstatic
```

## Performance Monitoring

### Development Profiling
```python
# Add to views for performance monitoring
import time
import logging

logger = logging.getLogger(__name__)

def my_view(request):
    start_time = time.time()
    # ... view logic ...
    end_time = time.time()
    logger.info(f"View executed in {end_time - start_time:.2f} seconds")
```

### Database Query Optimization
```python
# Use Django Debug Toolbar
# Or add query logging
LOGGING['loggers']['django.db.backends'] = {
    'handlers': ['console'],
    'level': 'DEBUG',
    'propagate': False,
}
```

## Contributing

### Branch Strategy
- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: Feature development
- `bugfix/*`: Bug fixes
- `hotfix/*`: Critical fixes

### Commit Convention
```
type(scope): description

feat(auth): add password reset functionality
fix(search): resolve semantic search timeout
docs(api): update endpoint documentation
test(properties): add unit tests for property model
```

### Pull Request Process
1. Create feature branch from `develop`
2. Implement changes with tests
3. Run code quality checks
4. Submit PR with description
5. Address review feedback
6. Merge after approval
