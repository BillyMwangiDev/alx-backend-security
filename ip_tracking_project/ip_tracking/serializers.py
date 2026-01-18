"""
Serializers for IP Tracking API
"""
from rest_framework import serializers
from .models import RequestLog, BlockedIP, SuspiciousIP


class RequestLogSerializer(serializers.ModelSerializer):
    """Serializer for RequestLog model"""
    
    class Meta:
        model = RequestLog
        fields = ['id', 'ip_address', 'timestamp', 'path', 'country', 'city']
        read_only_fields = ['id', 'timestamp']


class BlockedIPSerializer(serializers.ModelSerializer):
    """Serializer for BlockedIP model"""
    
    class Meta:
        model = BlockedIP
        fields = ['id', 'ip_address', 'blocked_at', 'reason']
        read_only_fields = ['id', 'blocked_at']


class SuspiciousIPSerializer(serializers.ModelSerializer):
    """Serializer for SuspiciousIP model"""
    
    class Meta:
        model = SuspiciousIP
        fields = ['id', 'ip_address', 'reason', 'detected_at', 'flagged']
        read_only_fields = ['id', 'detected_at']
