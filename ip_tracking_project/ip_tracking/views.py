from django.shortcuts import render
from django.http import JsonResponse
from .models import RequestLog
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit


def index(request):
    """Main view that displays request logs."""
    recent_requests = RequestLog.objects.all()[:50]
    return render(request, 'ip_tracking/index.html', {
        'requests': recent_requests,
        'total_requests': RequestLog.objects.count()
    })


@require_http_methods(['POST'])
@ratelimit(key='ip', rate='5/m', method='POST')
def login_view(request):
    """
    Simulated login view with rate limiting.
    Anonymous users are limited to 5 requests per minute.
    """
    # Check if rate limited
    if getattr(request, 'limited', False):
        return JsonResponse({
            'error': 'Too many requests. Please try again later.'
        }, status=429)
    
    return JsonResponse({
        'message': 'Login endpoint',
        'authenticated': request.user.is_authenticated
    })


@require_http_methods(["POST"])
@ratelimit(key='user_or_ip', rate='10/m', method='POST')
def authenticated_action(request):
    """
    Action with different limits for authenticated users.
    Authenticated users: 10 requests/minute.
    Anonymous users: 5 requests/minute based on IP address.
    """
    if getattr(request, 'limited', False):
        return JsonResponse({
            'error': 'Rate limit exceeded'
        }, status=429)
    
    return JsonResponse({
        'message': 'Action completed',
        'user': str(request.user)
    })


def ratelimit_error(request, exception):
    """Custom error handler for rate limit exceeded."""
    return JsonResponse({
        'error': 'Rate limit exceeded. Please try again later.'
    }, status=429)