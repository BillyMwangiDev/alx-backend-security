from django.shortcuts import render
from django.http import JsonResponse
from .models import RequestLog

def index(request):
    """Main view that displays request logs."""
    recent_requests = RequestLog.objects.all()[:50]
    return render(request, 'ip_tracking/index.html', {
        'requests': recent_requests,
        'total_requests': RequestLog.objects.count()
    })
