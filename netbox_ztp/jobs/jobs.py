from napalm import get_network_driver

from netbox.plugins import get_plugin_config
from netbox_ztp.models import SourceDevice


class OnboardDevices:
    def __init__(self, object: SourceDevice):
        self.object = object

    def run(self):
        username = str(get_plugin_config('netbox_ztp', 'username'))
        password = str(get_plugin_config('netbox_ztp', 'password'))
        if not username or not password:
            print("[ERROR] Missing username or password for ZTP plugin configuration")
            return
        if not self.object.device.primary_ip4:
            print(f"[ERROR] Device {self.object.device.name} does not have a primary IPv4 address")
            return

        interface_name = self.object.interface.name if self.object.interface else None
        if interface_name:
            print(
                f"[DEBUG] Running job on device {self.object.device.name} "
                f"with IP: {self.object.device.primary_ip4} using interface {interface_name}"
            )
        else:
            print(
                f"[DEBUG] Running job on device {self.object.device.name} "
                f"with IP: {self.object.device.primary_ip4}"
            )

        driver = get_network_driver('junos')
        connection = driver(hostname='bkbla101-esw1', username=username, password=password)
        connection.open()
        print("[DEBUG] Successfully connected to device 'bkbla101-esw1'")
        arp_entries = connection.get_arp_table()
        if interface_name:
            arp_entries = [
                entry for entry in arp_entries
                if str(
                    entry.get('interface', entry.get('interface_name', entry.get('ifname', '')))
                ).lower() == interface_name.lower()
            ]
        print(
            f"[DEBUG] Retrieved ARP entries for interface '{interface_name or 'all interfaces'}': "
            f"{arp_entries}"
        )
