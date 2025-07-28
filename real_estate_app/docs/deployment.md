# Production Deployment Guide

## Overview
This guide covers deploying the Real Estate Application to production environments using modern cloud platforms and containerization.

## Deployment Options

### 1. Container Deployment (Recommended)
- **Docker + Kubernetes**: Scalable microservices
- **Docker Compose**: Simple multi-container setup
- **Cloud Container Services**: AWS ECS, Google Cloud Run, Azure Container Instances

### 2. Platform as a Service (PaaS)
- **Heroku**: Simple deployment with addons
- **Railway**: Modern PaaS with Git integration
- **DigitalOcean App Platform**: Managed deployment

### 3. Virtual Private Server (VPS)
- **AWS EC2**: Full control with scalability
- **DigitalOcean Droplets**: Cost-effective VPS
- **Linode**: Developer-friendly VPS

## Prerequisites

### Infrastructure Requirements
- **CPU**: 2+ cores (4+ recommended)
- **RAM**: 4GB minimum (8GB+ recommended)
- **Storage**: 20GB SSD minimum
- **Network**: Public IP with HTTPS support

### External Services
- **Database**: PostgreSQL 13+ or MySQL 8+
- **Redis**: 6.0+ for caching and channels
- **File Storage**: AWS S3, Google Cloud Storage, or CDN
- **Email Service**: SendGrid, AWS SES, or Mailgun
- **SSL Certificate**: Let's Encrypt or commercial CA

## Environment Configuration

### Production Settings
Create `settings/production.py`:

```python
from .base import *
import os
import dj_database_url
from django.core.management.utils import get_random_secret_key

# Security Settings
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', get_random_secret_key())
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database Configuration
DATABASES = {
    'default': dj_database_url.parse(
        os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Channel Layers (WebSocket)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [os.environ.get('REDIS_URL', 'redis://localhost:6379/0')],
        },
    },
}

# Static and Media Files
USE_S3 = os.environ.get('USE_S3', 'False').lower() == 'true'

if USE_S3:
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    
    # Static files
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    
    # Media files
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
else:
    # Local file storage
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@realestate.com')

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 31536000
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net", "cdnjs.cloudflare.com")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net", "cdnjs.cloudflare.com")
CSP_IMG_SRC = ("'self'", "data:", "*.amazonaws.com")

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/django.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
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
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Performance Settings
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

### Environment Variables
Create production `.env`:
```env
# Django Configuration
DJANGO_SETTINGS_MODULE=real_estate_app.settings.production
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://username:password@host:5432/database_name

# Redis
REDIS_URL=redis://username:password@host:6379/0

# AWS S3 (if using)
USE_S3=True
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1

# Email Service
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

## Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=real_estate_app.settings.production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python manage.py check --database default || exit 1

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "real_estate_app.wsgi:application"]
```

### Docker Compose (Production)
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/realestate
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: realestate
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/var/www/static
      - media_volume:/var/www/media
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped

  celery:
    build: .
    command: celery -A real_estate_app worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/realestate
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped

  celery-beat:
    build: .
    command: celery -A real_estate_app beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/realestate
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
```

### Nginx Configuration
```nginx
upstream django {
    server web:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;

    client_max_body_size 20M;

    location / {
        proxy_pass http://django;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header Host $host;
        proxy_redirect off;
    }

    location /static/ {
        alias /var/www/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/media/;
        expires 1y;
        add_header Cache-Control "public";
    }

    location /ws/ {
        proxy_pass http://django;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}
```

## Kubernetes Deployment

### Deployment Manifest
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: realestate-web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: realestate-web
  template:
    metadata:
      labels:
        app: realestate-web
    spec:
      containers:
      - name: web
        image: your-registry/realestate:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: realestate-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: realestate-secrets
              key: redis-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: realestate-service
spec:
  selector:
    app: realestate-web
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## CI/CD Pipeline

### GitHub Actions
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install coverage
    
    - name: Run tests
      run: |
        coverage run --source='.' manage.py test
        coverage xml
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost/postgres
        REDIS_URL: redis://localhost:6379/0
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{ secrets.DOCKER_REGISTRY }}/realestate:latest
    
    - name: Deploy to production
      run: |
        # Deploy using your preferred method
        # kubectl, docker-compose, etc.
```

## Database Migration

### Production Migration Strategy
```bash
# 1. Backup current database
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Run migrations with zero downtime
python manage.py migrate --run-syncdb

# 3. Collect static files
python manage.py collectstatic --noinput

# 4. Restart application servers
# Rolling restart for zero downtime
```

## Monitoring & Observability

### Health Check Endpoint
Add to `urls.py`:
```python
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    try:
        # Check database
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Check Redis
        from django.core.cache import cache
        cache.set('health_check', 'ok', 30)
        
        return JsonResponse({'status': 'healthy'})
    except Exception as e:
        return JsonResponse({'status': 'unhealthy', 'error': str(e)}, status=500)
```

### Prometheus Metrics
```python
# Add to settings
INSTALLED_APPS += ['django_prometheus']
MIDDLEWARE = ['django_prometheus.middleware.PrometheusBeforeMiddleware'] + MIDDLEWARE
MIDDLEWARE += ['django_prometheus.middleware.PrometheusAfterMiddleware']
```

## Security Checklist

### Pre-deployment Security
- [ ] Update all dependencies
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Configure security headers
- [ ] Set up Web Application Firewall (WAF)
- [ ] Enable database encryption at rest
- [ ] Configure VPN for database access
- [ ] Set up intrusion detection
- [ ] Configure automated backups
- [ ] Enable audit logging
- [ ] Implement rate limiting

### Post-deployment Security
- [ ] Run security scan
- [ ] Test backup restoration
- [ ] Verify monitoring alerts
- [ ] Check log aggregation
- [ ] Test incident response procedures

## Performance Optimization

### Database Optimization
```python
# Connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'realestate',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'MAX_CONNS': 20,
            'sslmode': 'require',
        }
    }
}
```

### Caching Strategy
```python
# Redis caching
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            }
        }
    }
}
```

## Backup Strategy

### Automated Backups
```bash
#!/bin/bash
# backup_script.sh

DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/backups"

# Database backup
pg_dump $DATABASE_URL > $BACKUP_DIR/db_backup_$DATE.sql

# Media files backup
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /app/media/

# Upload to S3
aws s3 cp $BACKUP_DIR/db_backup_$DATE.sql s3://your-backup-bucket/database/
aws s3 cp $BACKUP_DIR/media_backup_$DATE.tar.gz s3://your-backup-bucket/media/

# Cleanup old backups (keep last 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### Cron Schedule
```bash
# Daily backup at 2 AM
0 2 * * * /path/to/backup_script.sh

# Weekly full backup on Sunday at 1 AM
0 1 * * 0 /path/to/full_backup_script.sh
```

## Troubleshooting

### Common Issues
1. **502 Bad Gateway**: Check application logs and ensure Django is running
2. **Database Connection Error**: Verify database credentials and network connectivity
3. **Static Files Not Loading**: Check STATIC_URL and run collectstatic
4. **WebSocket Connection Failed**: Verify Redis connection and channel layer configuration
5. **High Memory Usage**: Check for memory leaks and optimize queries

### Log Analysis
```bash
# View application logs
docker-compose logs -f web

# Database query analysis
tail -f /var/log/postgresql/postgresql.log

# Nginx access logs
tail -f /var/log/nginx/access.log

# Redis logs
redis-cli monitor
```
