"""
Celery configuration for ip_tracking_project.

This module initializes the Celery application and configures it
to work with Django settings and auto-discover tasks.
"""
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

# Create the Celery app instance
app = Celery('ip_tracking_project')

# Load configuration from Django settings, using a namespace 'CELERY'
# This means all Celery config options must be specified in settings.py
# with a 'CELERY_' prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
# This will look for tasks.py files in each app
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery setup."""
    print(f'Request: {self.request!r}')
