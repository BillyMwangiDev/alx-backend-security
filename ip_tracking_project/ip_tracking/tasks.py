from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from .models import RequestLog, SuspiciousIP

@shared_task
def detect_anomalies():
    """
    Detect suspicious IP activity:
    - IPs with more than 100 requests in the last hour
    - IPs accessing sensitive paths repeatedly
    """
    one_hour_ago = timezone.now() - timedelta(hours=1)
    
    # Find IPs with excessive requests
    excessive_ips = (
        RequestLog.objects
        .filter(timestamp__gte=one_hour_ago)
        .values('ip_address')
        .annotate(request_count=Count('id'))
        .filter(request_count__gt=100)
    )
    
    for item in excessive_ips:
        ip = item['ip_address']
        count = item['request_count']
        
        SuspiciousIP.objects.get_or_create(
            ip_address=ip,
            defaults={
                'reason': f'Excessive requests: {count} requests in the last hour'
            }
        )
    
    # Find IPs accessing sensitive paths
    sensitive_paths = ['/admin', '/login', '/api/login']
    
    for path in sensitive_paths:
        sensitive_ips = (
            RequestLog.objects
            .filter(timestamp__gte=one_hour_ago, path__startswith=path)
            .values('ip_address')
            .annotate(access_count=Count('id'))
            .filter(access_count__gt=10)  # More than 10 attempts
        )
        
        for item in sensitive_ips:
            ip = item['ip_address']
            count = item['access_count']
            
            SuspiciousIP.objects.get_or_create(
                ip_address=ip,
                defaults={
                    'reason': f'Multiple attempts to access {path}: {count} times in the last hour'
                }
            )
    
    return f"Anomaly detection completed at {timezone.now()}"