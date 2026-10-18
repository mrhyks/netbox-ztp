from napalm import get_network_driver

from netbox.plugins import get_plugin_config
from netbox_ztp.models import SourceDevice, ZTPLog


class OnboardDevices:
    def __init__(self, source_device: SourceDevice):
        self.source_device = source_device

    def _log(self, level, message, ip_address=None, serial_number=''):
        ZTPLog.objects.create(
            source_device=self.source_device,
            level=level,
            ip_address=ip_address,
            serial_number=serial_number,
            message=message,
        )

    def run(self):
        username = get_plugin_config('netbox_ztp', 'username')
        password = get_plugin_config('netbox_ztp', 'password')
        zeroday_username = get_plugin_config('netbox_ztp', 'zeroday_username')
        zeroday_password = get_plugin_config('netbox_ztp', 'zeroday_password')
        optional_args = get_plugin_config('netbox_ztp', 'optional_args') or {}

        if not username or not password:
            message = '[ERROR] Missing username or password for ZTP plugin configuration'
            self._log('error', message)
            print(message)
            return
        if not self.source_device.device.primary_ip4:
            message = f"[ERROR] Device {self.source_device.device.name} does not have a primary IPv4 address"
            self._log('error', message)
            print(message)
            return

        interface_name = self.source_device.interface.name if self.source_device.interface else None
        if interface_name:
            message = (
                f"[DEBUG] Running job on device {self.source_device.device.name} "
                f"with IP: {self.source_device.device.primary_ip4} using interface {interface_name}"
            )
        else:
            message = (
                f"[DEBUG] Running job on device {self.source_device.device.name} "
                f"with IP: {self.source_device.device.primary_ip4}"
            )
        self._log('info', message)
        print(message)

        driver_name = str(self.source_device.device.device_type.manufacturer.slug).lower()
        driver_name = driver_name.replace('juniper', 'junos').replace('cisco', 'ios')
        driver = get_network_driver(driver_name)
        connection = driver(
            hostname=str(self.source_device.device.name),
            username=username,
            password=password,
            optional_args=optional_args,
        )
        connection.open()
        message = f"[DEBUG] Successfully connected to device '{self.source_device.device.name}'"
        self._log('success', message)
        print(message)

        arp_entries = connection.get_arp_table()
        if interface_name:
            arp_entries = [
                entry for entry in arp_entries
                if str(
                    entry.get('interface', entry.get('interface_name', entry.get('ifname', '')))
                ).lower() == interface_name.lower()
            ]
        if self.source_device.ip_range:
            start_range = str(self.source_device.ip_range.start_address).split('/')[0]
            end_range = str(self.source_device.ip_range.end_address).split('/')[0]
            arp_entries = [
                entry for entry in arp_entries
                if start_range <= str(entry.get('ip', '')) <= end_range
            ]

        message = (
            f"[DEBUG] Retrieved ARP entries for interface '{interface_name or 'all interfaces'}' and range '{self.source_device.ip_range or 'all addresses'}': "
            f"{arp_entries}"
        )
        self._log('info', message)
        print(message)

        for entry in arp_entries:
            ip_value = str(entry.get('ip') or entry.get('address') or entry.get('ip_address') or '')
            if not ip_value:
                continue
            try:
                onboarded_driver = get_network_driver(
                    self.source_device.onboarded_devices_vendor.slug.replace('juniper', 'junos').replace('cisco', 'ios')
                )
                onboarded_connection = onboarded_driver(
                    hostname=ip_value,
                    username=zeroday_username,
                    password=zeroday_password,
                    optional_args=optional_args,
                )
                onboarded_connection.open()
                facts = onboarded_connection.get_facts() or {}
                serial_number = str(facts.get('serial_number') or facts.get('serial') or '')
                message = f"[DEBUG] Successfully connected to onboarded device with IP '{ip_value}' using driver '{self.source_device.onboarded_devices_vendor.slug.replace('juniper', 'junos').replace('cisco', 'ios')}'"
                self._log('success', message, ip_address=ip_value, serial_number=serial_number)
                print(message)
                print(facts)
                onboarded_connection.close()
            except Exception as exc:
                message = (
                    f"[ERROR] Failed to connect to onboarded device with IP '{ip_value}' "
                    f"using driver '{driver_name}': {exc}"
                )
                self._log('error', message, ip_address=ip_value)
                print(message)
                continue
