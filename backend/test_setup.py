#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adoptiq.settings')
os.environ['SECRET_KEY'] = 'test-secret-key-for-validation'
os.environ['DEBUG'] = 'True'
os.environ['DB_NAME'] = 'test_db'
os.environ['DB_USER'] = 'test'
os.environ['DB_PASSWORD'] = 'test'
os.environ['DB_HOST'] = 'localhost'
os.environ['REDIS_URL'] = 'redis://localhost:6379/0'
os.environ['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'

django.setup()

from django.core import management
from django.conf import settings

print("✓ Django setup successful")
print(f"✓ Installed apps: {len(settings.INSTALLED_APPS)}")
print(f"✓ Middleware: {len(settings.MIDDLEWARE)}")
print(f"✓ Database backend: {settings.DATABASES['default']['ENGINE']}")
print("✓ All imports successful")
print("\n✅ Backend configuration is valid!")
