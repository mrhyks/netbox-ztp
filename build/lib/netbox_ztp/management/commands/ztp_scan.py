from django.core.management.base import BaseCommand

from netbox_ztp.tasks import run_ztp_scan


class Command(BaseCommand):
    help = "Scan ARP tables for unknown devices, onboard them over SSH, and log the results."

    def handle(self, *args, **options):
        run_ztp_scan()
        self.stdout.write(self.style.SUCCESS("ZTP scan completed."))
