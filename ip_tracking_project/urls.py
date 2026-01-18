"""
URL configuration for ip_tracking_project project.
"""
from django.contrib import admin
from django.urls import path
from ip_tracking import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('api/', include('ip_tracking.urls')),
    
]
