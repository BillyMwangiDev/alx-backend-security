"""
Django management command to block IP addresses.
Usage: python manage.py block_ip <ip_address> [--reason "reason text"]
"""
from django.core.management.base import BaseCommand, CommandError
from ip_tracking.models import BlockedIP
import ipaddress


class Command(BaseCommand):
    help = 'Block an IP address by adding it to the BlockedIP model'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'ip_address',
            type=str,
            help='The IP address to block (IPv4 or IPv6)'
        )
        parser.add_argument(
            '--reason',
            type=str,
            default='Manually blocked',
            help='Reason for blocking the IP address'
        )
    
    def handle(self, *args, **options):
        ip_address = options['ip_address']
        reason = options['reason']
        
        # Validate IP address
        try:
            ipaddress.ip_address(ip_address)
        except ValueError:
            raise CommandError(f'"{ip_address}" is not a valid IP address')
        
        # Check if IP is already blocked
        if BlockedIP.objects.filter(ip_address=ip_address).exists():
            self.stdout.write(
                self.style.WARNING(f'IP address {ip_address} is already blocked')
            )
            return
        
        # Block the IP
        try:
            blocked_ip = BlockedIP.objects.create(
                ip_address=ip_address,
                reason=reason
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully blocked IP: {ip_address}\n'
                    f'Reason: {reason}'
                )
            )
        except Exception as e:
            raise CommandError(f'Failed to block IP: {str(e)}')
