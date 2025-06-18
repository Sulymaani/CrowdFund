"""
Production optimizations for the CrowdFund application.

This module contains settings and configurations that optimize
the application for production environments, focusing on performance,
security, and scalability.
"""

# --- Performance Optimizations ---

# Template caching
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]

# Database query optimizations
DATABASE_ROUTERS = []  # Add custom routers if needed

# Connection pooling already configured in production.py

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'TIMEOUT': 300,  # 5 minutes default
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'IGNORE_EXCEPTIONS': True,
        }
    }
}

# Cache middleware
MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',
    # ... existing middleware ...
    'django.middleware.cache.FetchFromCacheMiddleware',
]

# Session cache
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Cache timeout settings
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 600
CACHE_MIDDLEWARE_KEY_PREFIX = 'crowdfund'

# --- Security Optimizations ---

# Add Django security middleware if not already present
if 'django.middleware.security.SecurityMiddleware' not in MIDDLEWARE:
    MIDDLEWARE.insert(0, 'django.middleware.security.SecurityMiddleware')

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net", "https://code.jquery.com")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net")
CSP_IMG_SRC = ("'self'", "data:", "https://cdn.jsdelivr.net")
CSP_FONT_SRC = ("'self'", "data:", "https://cdn.jsdelivr.net")

# Other security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# --- Compression and Minification ---

# Enable GZip compression
MIDDLEWARE.insert(
    MIDDLEWARE.index('django.middleware.security.SecurityMiddleware') + 1,
    'django.middleware.gzip.GZipMiddleware'
)

# Static files compression
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# --- Logging Enhancements ---

# Log slow database queries
LOGGING['loggers']['django.db.backends'] = {
    'handlers': ['console'],
    'level': 'WARNING',  # Change to DEBUG to see all queries
    'propagate': False,
}

# Add Sentry integration if available
try:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    
    sentry_sdk.init(
        dsn=os.environ.get('SENTRY_DSN', ''),
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.2,  # Adjust based on traffic
        send_default_pii=False
    )
except ImportError:
    pass  # Sentry not installed

# --- Background Task Processing ---

# Use Celery for background tasks if available
try:
    import celery
    
    CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = TIME_ZONE
    
    # Recommended Celery settings
    CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
    CELERY_TASK_TIME_LIMIT = 60 * 5  # 5 minutes
    CELERY_TASK_SOFT_TIME_LIMIT = 60 * 2  # 2 minutes
except ImportError:
    pass  # Celery not installed

# --- API Optimizations ---

# REST Framework settings for production
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# --- Admin Optimizations ---

# Limit admin site functionality for production
ADMIN_SITE_HEADER = "CrowdFund Administration"
ADMIN_SITE_TITLE = "CrowdFund Admin Portal"
ADMIN_INDEX_TITLE = "Site Administration"

# Restrict admin access by IP if needed
ADMIN_IP_ALLOWLIST = os.environ.get('ADMIN_IP_ALLOWLIST', '').split(',')

if ADMIN_IP_ALLOWLIST and ADMIN_IP_ALLOWLIST[0]:
    # Add middleware to restrict admin access by IP
    MIDDLEWARE.append('core.middleware.AdminIPRestrictionMiddleware')

# --- File Storage Optimization ---

# Use cloud storage for media files if available
try:
    from storages.backends.s3boto3 import S3Boto3Storage
    
    # AWS settings
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_DEFAULT_ACL = 'public-read'
    
    # Media storage
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
except ImportError:
    pass  # AWS storage not installed
