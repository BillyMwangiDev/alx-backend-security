"""
URL configuration for ip_tracking_project project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from ip_tracking import views

# Swagger/OpenAPI Schema
schema_view = get_schema_view(
    openapi.Info(
        title="IP Tracking & Security API",
        default_version='v1',
        description="""
# IP Tracking & Security System API

Enterprise-grade IP tracking, geolocation, and anomaly detection for Django applications.

## Features

- **IP Logging:** Track all incoming requests with geolocation data
- **IP Blacklisting:** Block malicious IP addresses
- **Rate Limiting:** Prevent abuse with configurable limits
- **Anomaly Detection:** Identify suspicious patterns automatically
- **Analytics:** Comprehensive statistics and insights

## Authentication

Most endpoints are publicly accessible for demonstration purposes.
In production, use Token Authentication or OAuth2.

## Rate Limits

- Anonymous users: 5 requests/minute
- Authenticated users: 10 requests/minute
        """,
        terms_of_service="https://github.com/BillyMwangiDev/alx-backend-security",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="ALX Backend Security"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Main dashboard
    path('', views.index, name='index'),
    
    # API endpoints
    path('api/v1/', include('ip_tracking.api_urls')),
    path('api/', include('ip_tracking.urls')),  # Legacy endpoints
    
    # Swagger/OpenAPI Documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Redirect root API to Swagger
    path('api-docs/', RedirectView.as_view(url='/swagger/', permanent=False)),
]

