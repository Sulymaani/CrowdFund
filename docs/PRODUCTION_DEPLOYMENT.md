# CrowdFund Production Deployment Guide

## Overview

This document outlines the steps and best practices for deploying the CrowdFund application to a production environment. Following these guidelines will help ensure that your deployment is secure, performant, and maintainable.

## Pre-Deployment Checklist

Before deploying to production, ensure you have completed the following:

### Security

- [ ] `DEBUG` is set to `False` in production settings
- [ ] Generate a new random `SECRET_KEY` for production
- [ ] Configure proper `ALLOWED_HOSTS` with your domain(s)
- [ ] Ensure all sensitive data is stored in environment variables (not in code)
- [ ] Enable HTTPS with proper SSL/TLS certificates
- [ ] Review Django security best practices (https://docs.djangoproject.com/en/stable/topics/security/)
- [ ] Set up proper CORS headers if your API is accessed from different domains
- [ ] Configure CSRF protection properly
- [ ] Ensure password policies enforce sufficient complexity

### Performance

- [ ] Configure database connection pooling
- [ ] Set up caching for templates, queries, and sessions
- [ ] Configure static files to be served by a CDN or dedicated web server
- [ ] Enable database query optimization (indexes, etc.)
- [ ] Configure appropriate timeouts for all services
- [ ] Set up proper logging and monitoring
- [ ] Configure appropriate WSGI/ASGI server settings (workers, threads, etc.)

### Database

- [ ] Review and apply all migrations
- [ ] Add database indexes for commonly queried fields
- [ ] Set up regular database backups
- [ ] Configure database connection pooling
- [ ] Optimize database settings for production use

### Static Files

- [ ] Run `collectstatic` to gather all static files
- [ ] Configure static files to be served by Nginx, CDN, or other static file server
- [ ] Set up proper caching headers for static assets
- [ ] Minify and bundle CSS/JS files
- [ ] Optimize image sizes and formats

### Emails and Notifications

- [ ] Configure a production email backend (SMTP, SendGrid, etc.)
- [ ] Test all transactional emails
- [ ] Set up error alerts and notifications

### Logging and Monitoring

- [ ] Configure appropriate logging levels
- [ ] Set up log rotation
- [ ] Configure error reporting service (Sentry, etc.)
- [ ] Set up application and server monitoring

## Production Settings

Create a production settings file (`crowdfund/settings/production.py`) with the following configurations:

```python
from .base import *
import os

# Security
DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = ['.yourcrowdfunddomain.com']

# HTTPS/SSL
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,  # connection pooling
    }
}

# Caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
    }
}

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'noreply@yourcrowdfunddomain.com'

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
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django-errors.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}

# Static and Media files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# If using a CDN
# STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
```

## Deployment Options

### Option 1: Traditional VPS/Dedicated Server

1. **Server Setup**
   - Install required packages: Python, PostgreSQL, Redis, Nginx, etc.
   - Configure firewall to only allow necessary ports
   - Set up systemd services for Gunicorn/uWSGI

2. **Application Deployment**
   - Clone code from repository
   - Create virtual environment and install dependencies
   - Apply migrations
   - Collect static files
   - Configure Gunicorn/uWSGI
   - Set up Nginx as reverse proxy

3. **Example Nginx Configuration**

```nginx
server {
    listen 80;
    server_name yourcrowdfunddomain.com www.yourcrowdfunddomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name yourcrowdfunddomain.com www.yourcrowdfunddomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourcrowdfunddomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourcrowdfunddomain.com/privkey.pem;
    
    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_session_cache shared:SSL:10m;
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data: https://cdn.jsdelivr.net; font-src 'self' data: https://cdn.jsdelivr.net;";
    
    # Static files
    location /static/ {
        alias /path/to/crowdfund/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }
    
    # Media files
    location /media/ {
        alias /path/to/crowdfund/mediafiles/;
        expires 30d;
    }
    
    # Proxy to Gunicorn
    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://unix:/path/to/crowdfund/crowdfund.sock;
        proxy_redirect off;
        proxy_buffering off;
    }
}
```

4. **Example Gunicorn Configuration**

Create a systemd service file `/etc/systemd/system/crowdfund.service`:

```ini
[Unit]
Description=CrowdFund Gunicorn daemon
After=network.target

[Service]
User=crowdfund
Group=www-data
WorkingDirectory=/path/to/crowdfund
ExecStart=/path/to/crowdfund/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/path/to/crowdfund/crowdfund.sock \
          crowdfund.wsgi:application
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

### Option 2: Docker Deployment

1. **Create a Dockerfile**

```dockerfile
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=crowdfund.settings.production

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project files
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD gunicorn crowdfund.wsgi:application --bind 0.0.0.0:8000
```

2. **Create docker-compose.yml**

```yaml
version: '3'

services:
  db:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    env_file:
      - ./.env.db
    restart: always
    
  redis:
    image: redis:7
    restart: always
    
  web:
    build: .
    restart: always
    depends_on:
      - db
      - redis
    env_file:
      - ./.env
    volumes:
      - ./mediafiles:/app/mediafiles
      - ./staticfiles:/app/staticfiles
      
  nginx:
    image: nginx:1.23
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./nginx/ssl:/etc/nginx/ssl
      - ./staticfiles:/var/www/static
      - ./mediafiles:/var/www/media
    depends_on:
      - web
    restart: always

volumes:
  postgres_data:
```

### Option 3: Platform as a Service (PaaS)

For simpler deployments, consider using:

- Heroku
- DigitalOcean App Platform
- AWS Elastic Beanstalk
- Google App Engine
- Render.com

Each platform has specific deployment instructions, but they generally involve:
1. Setting up the appropriate buildpack/runtime
2. Configuring environment variables
3. Setting up database and cache add-ons
4. Configuring custom domains and SSL

## Post-Deployment Verification

After deploying, verify the following:

1. **Security Check**
   - Run a security scan (e.g., with [Django Security Check](https://pypi.org/project/django-security-check/))
   - Test HTTPS is working properly
   - Check security headers are properly set
   
2. **Functionality Check**
   - Test all critical user flows (registration, login, campaign creation, donations)
   - Verify email functionality
   - Check payment processing
   
3. **Performance Check**
   - Test page load speeds
   - Verify static assets are being served correctly
   - Check database query performance
   
4. **Monitoring Check**
   - Verify logs are being generated correctly
   - Set up alerts for critical errors
   - Monitor server resource usage

## Maintenance Routine

Establish a regular maintenance routine:

1. **Weekly**
   - Review error logs
   - Check server resource usage
   - Apply security patches if available
   
2. **Monthly**
   - Database maintenance (vacuum, reindex)
   - Review and clean up old sessions
   - Check SSL certificates expiration
   
3. **Quarterly**
   - Upgrade dependencies
   - Review and optimize slow queries
   - Perform security audit

## Backup Strategy

Implement a robust backup strategy:

1. **Database Backups**
   - Daily automated backups
   - Weekly full backups
   - Store backups in multiple locations
   
2. **File Backups**
   - Backup user-uploaded media files
   - Backup configuration files
   
3. **Test Restores**
   - Regularly test restoring from backups
   - Document the restore procedure

## Scaling Considerations

As your application grows, consider:

1. **Database Scaling**
   - Read replicas for query-heavy operations
   - Connection pooling
   - Sharding for very large datasets
   
2. **Application Scaling**
   - Load balancing across multiple application servers
   - Microservices architecture for specific components
   - Serverless functions for background jobs
   
3. **Caching Strategy**
   - Page caching
   - Query result caching
   - Fragment caching
   
4. **Content Delivery**
   - Global CDN for static assets
   - Edge caching for dynamic content
