from django.utils.deprecation import MiddlewareMixin
from ipware import get_client_ip
from .models import RequestLog

class IPLoggingMiddleware(MiddlewareMixin):
  def process_request(self, request):
    
    #Get the client's IP address
    client_ip,is_routable = get_client_ip(request)
    
    if client_ip:
      #log the request
      RequestLog.objects.create(
        ip_address=client_ip,
        path=request.path
      )
      
      
    return None