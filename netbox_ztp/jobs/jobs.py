from napalm import get_network_driver

from netbox.plugins import get_plugin_config
from netbox_ztp.models import SourceDevice

import ipaddress

class OnboardDevices:
    def __init__(self, source_device: SourceDevice):
        self.source_device = source_device

    def run(self):
        username = str(get_plugin_config('netbox_ztp', 'username'))
        password = str(get_plugin_config('netbox_ztp', 'password'))
        zeroday_username = str(get_plugin_config('netbox_ztp', 'zeroday_username'))
        zeroday_password = str(get_plugin_config('netbox_ztp', 'zeroday_password'))
        optional_args = get_plugin_config('netbox_ztp', 'optional_args')

        if not username or not password:
            print('[ERROR] Missing username or password for ZTP plugin configuration')
            return
        if not self.source_device.device.primary_ip4:
            print(f"[ERROR] Device {self.source_device.device.name} does not have a primary IPv4 address")
            return

        interface_name = self.source_device.interface.name if self.source_device.interface else None
        if interface_name:
            print(
                f"[DEBUG] Running job on device {self.source_device.device.name} "
                f"with IP: {self.source_device.device.primary_ip4} using interface {interface_name}"
            )
        else:
            print(
                f"[DEBUG] Running job on device {self.source_device.device.name} "
                f"with IP: {self.source_device.device.primary_ip4}"
            )

        driver_name = str(self.source_device.device.device_type.manufacturer.slug).lower()
        driver_name = driver_name.replace('juniper', 'junos').replace('cisco', 'ios')
        driver = get_network_driver(driver_name)
        connection = driver(hostname=str(self.source_device.device.name), username=username, password=password, optional_args=optional_args)
        connection.open()
        print(f"[DEBUG] Successfully connected to device '{self.source_device.device.name}'")

        arp_entries = connection.get_arp_table()
        if interface_name:
            arp_entries = [
                entry for entry in arp_entries
                if str(
                    entry.get('interface', entry.get('interface_name', entry.get('ifname', '')))
                ).lower() == interface_name.lower()
            ]
        if self.source_device.ip_range:
            arp_entries = [
                entry for entry in arp_entries
                if ipaddress.ip_address(str(entry.get('ip') or entry.get('address') or entry.get('ip_address') or '')) in ipaddress.ip_network(self.source_device.ip_range)
            ]

        print(
            f"[DEBUG] Retrieved ARP entries for interface '{interface_name or 'all interfaces'}' and range '{self.source_device.ip_range or 'all addresses'}': "
            f"{arp_entries}"
        )

        drivers = ['ios', 'junos']
        for entry in arp_entries:
            ip_value = str(entry.get('ip') or entry.get('address') or entry.get('ip_address') or '')
            if not ip_value:
                continue
            for driver in drivers:
                try:
                    onboarded_driver = get_network_driver(driver)
                    onboarded_connection = onboarded_driver(
                        hostname=ip_value,
                        username=zeroday_username,
                        password=zeroday_password,
                        optional_args=optional_args,
                    )
                    onboarded_connection.open()
                    print(f"[DEBUG] Successfully connected to onboarded device with IP '{ip_value}' using driver '{driver}'")
                    print(onboarded_connection.get_facts())
                    onboarded_connection.close()
                    break
                except Exception as exc:
                    print(f"[ERROR] Failed to connect to onboarded device with IP '{ip_value}' using driver '{driver}': {exc}")
                    continue
