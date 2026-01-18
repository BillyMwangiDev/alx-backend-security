"""
API URLs for IP Tracking
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import RequestLogViewSet, BlockedIPViewSet, SuspiciousIPViewSet

router = DefaultRouter()
router.register(r'logs', RequestLogViewSet, basename='requestlog')
router.register(r'blocked', BlockedIPViewSet, basename='blockedip')
router.register(r'suspicious', SuspiciousIPViewSet, basename='suspiciousip')

urlpatterns = [
    path('', include(router.urls)),
]
