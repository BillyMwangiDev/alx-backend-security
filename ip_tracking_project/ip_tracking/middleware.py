from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.core.cache import cache
from ipware import get_client_ip
from .models import RequestLog, BlockedIP
import logging

logger = logging.getLogger(__name__)


class IPLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to:
    1. Log all incoming requests with IP, path, and timestamp
    2. Block requests from blacklisted IPs
    3. Add geolocation data (country, city) with caching
    """
    
    def process_request(self, request):
        # Get the client's IP address
        client_ip, is_routable = get_client_ip(request)
        
        if not client_ip:
            return None
        
        # Task 1: Check if IP is blocked (with error handling for missing tables)
        try:
            if BlockedIP.objects.filter(ip_address=client_ip).exists():
                logger.warning(f"Blocked IP attempted access: {client_ip}")
                return HttpResponseForbidden("Access denied. Your IP has been blocked.")
        except Exception as e:
            # If database tables don't exist yet, just log and continue
            logger.debug(f"Could not check blocked IPs: {e}")
        
        # Task 2: Get geolocation data with caching (24 hours)
        country, city = self._get_geolocation(client_ip)
        
        # Task 0: Log the request
        try:
            RequestLog.objects.create(
                ip_address=client_ip,
                path=request.path,
                country=country,
                city=city
            )
        except Exception as e:
            logger.error(f"Failed to log request: {e}")
        
        return None
    
    def _get_geolocation(self, ip_address):
        """
        Get geolocation data for an IP address with 24-hour caching.
        Uses geoip2 library (MaxMind GeoLite2 database).
        """
        cache_key = f'geolocation_{ip_address}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        country = None
        city = None
        
        try:
            # Try using geoip2 with maxminddb-geolite2
            from geolite2 import geolite2
            
            reader = geolite2.reader()
            if reader:
                match = reader.get(ip_address)
                if match:
                    country = match.get('country', {}).get('names', {}).get('en')
                    city = match.get('city', {}).get('names', {}).get('en')
                geolite2.close()
        except ImportError:
            logger.debug("geolite2 not available, geolocation disabled")
        except Exception as e:
            logger.debug(f"Geolocation lookup failed for {ip_address}: {e}")
        
        # Cache for 24 hours (86400 seconds)
        result = (country, city)
        cache.set(cache_key, result, 86400)
        
        return result