from napalm import get_network_driver

from napalm.base.base import NetworkDriver
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

    def get_arp_entries(self, username, password, optional_args):
        interface_name = (
            self.source_device.interface.name if self.source_device.interface else None
        )
        if interface_name:
            message = (
                f'Running job on device {self.source_device.device.name} '
                f'with IP: {self.source_device.device.primary_ip4} using interface {interface_name}'
            )
        else:
            message = (
                f'Running job on device {self.source_device.device.name} '
                f'with IP: {self.source_device.device.primary_ip4}'
            )
        self._log('info', message)
        print(message)

        driver_name = str(
            self.source_device.device.device_type.manufacturer.slug
        ).lower()
        driver_name = driver_name.replace('juniper', 'junos').replace('cisco', 'ios')
        driver = get_network_driver(driver_name)
        connection = driver(
            hostname=str(self.source_device.device.name),
            username=username,
            password=password,
            optional_args=optional_args,
        )
        connection.open()
        message = f"Successfully connected to device '{self.source_device.device.name}'"
        self._log('success', message)
        print(message)

        arp_entries = connection.get_arp_table()
        if interface_name:
            arp_entries = [
                entry
                for entry in arp_entries
                if str(
                    entry.get(
                        'interface',
                        entry.get('interface_name', entry.get('ifname', '')),
                    )
                ).lower()
                == interface_name.lower()
            ]
        if self.source_device.ip_range:
            start_range = str(self.source_device.ip_range.start_address).split('/')[0]
            end_range = str(self.source_device.ip_range.end_address).split('/')[0]
            arp_entries = [
                entry
                for entry in arp_entries
                if start_range <= str(entry.get('ip', '')) <= end_range
            ]

        message = (
            f"Retrieved ARP entries for interface '{interface_name or 'all interfaces'}' and range '{self.source_device.ip_range or 'all addresses'}': "
            f'{arp_entries}'
        )
        self._log('info', message)
        print(message)

    def connect_to_new_device(
        self, zeroday_username, zeroday_password, ip, optional_args
    ) -> NetworkDriver | None:
        driver_name = self.source_device.onboarded_devices_vendor.slug.replace(
            'juniper', 'junos'
        ).replace('cisco', 'ios')
        try:
            onboarded_driver = get_network_driver(driver_name)
            onboarded_connection = onboarded_driver(
                hostname=ip,
                username=zeroday_username,
                password=zeroday_password,
                optional_args=optional_args,
            )
            onboarded_connection.open()
            facts = onboarded_connection.get_facts() or {}
            serial_number = str(facts.get('serial_number') or facts.get('serial') or '')
            message = f"Successfully connected to onboarded device with IP '{ip}' using driver '{self.source_device.onboarded_devices_vendor.slug.replace('juniper', 'junos').replace('cisco', 'ios')}'"
            self._log('success', message, ip_address=ip, serial_number=serial_number)
            print(message)
            print(facts)
            onboarded_connection.close()

        except Exception as exc:  # noqa: BLE001
            message = (
                f"Failed to connect to onboarded device with IP '{ip}' "
                f"using driver '{driver_name}': {exc}"
            )
            self._log('error', message, ip_address=ip)
            print(message)

    def run(self):
        username = get_plugin_config('netbox_ztp', 'username')
        password = get_plugin_config('netbox_ztp', 'password')
        zeroday_username = get_plugin_config('netbox_ztp', 'zeroday_username')
        zeroday_password = get_plugin_config('netbox_ztp', 'zeroday_password')
        optional_args = get_plugin_config('netbox_ztp', 'optional_args') or {}

        if not username or not password:
            message = (
                'Missing username or password for ZTP plugin configuration'
            )
            self._log('error', message)
            print(message)
            return
        if not zeroday_username or not zeroday_password:
            message = 'Missing zeroday username or password for ZTP plugin configuration'
            self._log('error', message)
            print(message)
            return

        for entry in arp_entries:
            ip_value = str(
                entry.get('ip') or entry.get('address') or entry.get('ip_address') or ''
            )
            if not ip_value:
                continue

            connection = self.connect_to_new_device(zeroday_username, zeroday_password, ip_value, optional_args)

            if not connection:
                continue
