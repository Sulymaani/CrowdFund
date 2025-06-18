"""
Django settings package for CrowdFund project.
Default imports from the base settings and overrides based on environment.
"""
import os
from pathlib import Path

# Determine which environment settings to use based on DJANGO_ENV environment variable
# Default to development if not specified
env = os.environ.get('DJANGO_ENV', 'development')

# Import the appropriate settings module based on the environment
if env == 'production':
    from .production import *
else:
    from .development import *
