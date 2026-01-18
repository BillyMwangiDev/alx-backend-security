# Import Celery app only if celery is being used
# This allows the app to work without Celery workers on free tier
try:
    from .celery_app import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    # Celery not available or not needed (free tier deployment)
    pass