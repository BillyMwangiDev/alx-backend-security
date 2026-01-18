from django.contrib import admin
from .models import RequestLog, BlockedIP, SuspiciousIP

@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'path', 'country', 'city', 'timestamp']
    list_filter = ['country', 'timestamp']
    search_fields = ['ip_address', 'path']
    readonly_fields = ['ip_address', 'path', 'country', 'city', 'timestamp']

@admin.register(BlockedIP)
class BlockedIPAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'reason', 'blocked_at']
    search_fields = ['ip_address', 'reason']
    readonly_fields = ['blocked_at']

@admin.register(SuspiciousIP)
class SuspiciousIPAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'reason', 'flagged', 'detected_at']
    list_filter = ['flagged', 'detected_at']
    search_fields = ['ip_address', 'reason']
    readonly_fields = ['detected_at']
    actions = ['block_selected_ips']
    
    def block_selected_ips(self, request, queryset):
        for suspicious_ip in queryset:
            BlockedIP.objects.get_or_create(
                ip_address=suspicious_ip.ip_address,
                defaults={'reason': suspicious_ip.reason}
            )
        self.message_user(request, f"{queryset.count()} IPs have been blocked.")
    
    block_selected_ips.short_description = "Block selected suspicious IPs"
```