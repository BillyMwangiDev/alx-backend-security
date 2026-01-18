"""
API ViewSets for IP Tracking
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import RequestLog, BlockedIP, SuspiciousIP
from .serializers import RequestLogSerializer, BlockedIPSerializer, SuspiciousIPSerializer


class RequestLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing request logs.
    
    list: Get all request logs
    retrieve: Get a specific request log
    stats: Get request statistics
    """
    queryset = RequestLog.objects.all().order_by('-timestamp')
    serializer_class = RequestLogSerializer
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get request statistics"""
        total_requests = RequestLog.objects.count()
        unique_ips = RequestLog.objects.values('ip_address').distinct().count()
        
        # Last 24 hours stats
        last_24h = timezone.now() - timedelta(hours=24)
        recent_requests = RequestLog.objects.filter(timestamp__gte=last_24h).count()
        
        # Top countries
        top_countries = RequestLog.objects.exclude(
            country__isnull=True
        ).values('country').annotate(
            count=models.Count('id')
        ).order_by('-count')[:5]
        
        return Response({
            'total_requests': total_requests,
            'unique_ips': unique_ips,
            'requests_last_24h': recent_requests,
            'top_countries': list(top_countries)
        })


class BlockedIPViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing blocked IPs.
    
    list: Get all blocked IPs
    create: Block a new IP
    retrieve: Get details of a blocked IP
    update: Update blocked IP details
    destroy: Unblock an IP
    """
    queryset = BlockedIP.objects.all().order_by('-blocked_at')
    serializer_class = BlockedIPSerializer
    permission_classes = [permissions.AllowAny]  # Change to IsAdminUser in production
    
    @action(detail=True, methods=['post'])
    def unblock(self, request, pk=None):
        """Unblock an IP address"""
        blocked_ip = self.get_object()
        blocked_ip.delete()
        return Response(
            {'message': f'IP {blocked_ip.ip_address} has been unblocked'},
            status=status.HTTP_200_OK
        )


class SuspiciousIPViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing suspicious IPs.
    
    list: Get all suspicious IPs
    retrieve: Get details of a suspicious IP
    update: Update suspicious IP status
    block: Block a suspicious IP
    """
    queryset = SuspiciousIP.objects.all().order_by('-detected_at')
    serializer_class = SuspiciousIPSerializer
    permission_classes = [permissions.AllowAny]  # Change to IsAdminUser in production
    
    @action(detail=True, methods=['post'])
    def block(self, request, pk=None):
        """Block a suspicious IP"""
        suspicious_ip = self.get_object()
        
        # Check if already blocked
        if BlockedIP.objects.filter(ip_address=suspicious_ip.ip_address).exists():
            return Response(
                {'message': 'IP is already blocked'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Block the IP
        BlockedIP.objects.create(
            ip_address=suspicious_ip.ip_address,
            reason=suspicious_ip.reason
        )
        
        # Update flagged status
        suspicious_ip.flagged = False
        suspicious_ip.save()
        
        return Response(
            {'message': f'IP {suspicious_ip.ip_address} has been blocked'},
            status=status.HTTP_201_CREATED
        )


from django.db import models
