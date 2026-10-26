import re
import time

from django.contrib.contenttypes.models import ContentType
from napalm import get_network_driver
from napalm.base.base import NetworkDriver
from napalm.base.models import ARPTableDict, FactsDict

from dcim.models import Device, DeviceRole, DeviceType, Interface, MACAddress, Site
from extras.models import Tag
from ipam.models import IPAddress
from netbox.plugins import get_plugin_config
from netbox_ztp.models import OnboardedDevice, SoftwareAssignment, SourceDevice, ZTPLog


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
        print(message)

    def update_needed(self, version: str, onboarded_device: OnboardedDevice):
        assignment = SoftwareAssignment.objects.filter(
            device_types=onboarded_device.device.device_type
        ).first()
        self._log(
            'info',
            f'Checking if update is needed for device {onboarded_device.device.name}',
            ip_address=onboarded_device.device.primary_ip4.address.split('/')[0],
            serial_number=onboarded_device.device.serial,
        )
        self._log(
            'info',
            f'Found {"1" if assignment else "0"} software assignments for device {onboarded_device.device.name}',
            ip_address=onboarded_device.device.primary_ip4.address.split('/')[0],
            serial_number=onboarded_device.device.serial,
        )
        self._log('info', f'Current software version for device {onboarded_device.device.name} is {version} and required is {assignment.version if assignment else "N/A"}')
        return bool(assignment and assignment.version != version)

    def update_device(
        self, connection: NetworkDriver, onboarded_device: OnboardedDevice
    ) -> bool:
        assignment = SoftwareAssignment.objects.filter(
            device_types=onboarded_device.device.device_type
        ).first()
        if (
            self.source_device.onboarded_devices_vendor.slug.lower() == 'cisco'
            and assignment
        ):
            path = 'flash:/'
            commands = [
                'write memory',
                f'copy {assignment.file_path} {path}cisco_{assignment.version}.bin\n',
                f'install add file flash:/cisco_{assignment.version}.bin activate commit prompt-level none',
            ]
            self._log(
                'info', f'sending commands: {commands} to device {connection.hostname.split("/")[0]}'
            )
            connection.cli(commands)
            time.sleep(60)
            if not connection.is_alive().get('is_alive', True):
                self._log(
                    'info', f'Device {connection.hostname.split("/")[0]} is restarting to update.'
                )
                connection.close()
                return True
        elif (
            self.source_device.onboarded_devices_vendor.slug.lower() == 'juniper'
            and assignment
        ):
            path = '/var/tmp/'
            commands = [
                f'file copy {assignment.file_path} {path}juniper_{assignment.version}.tgz',
                f'request system software add {path}juniper_{assignment.version}.tgz no-validate',
            ]
            self._log(
                'info', f'sending commands: {commands} to device {connection.hostname.split("/")[0]}'
            )
            connection.cli(commands)
            time.sleep(60)
            if not connection.is_alive().get('is_alive', True):
                self._log(
                    'info', f'Device {connection.hostname.split("/")[0]} is restarting to update.'
                )
                connection.close()
                return True
        else:
            path = ''
            self._log(
                'info',
                f'No software assignment found for device {connection.hostname.split("/")[0]}.',
            )
            return False
        return False

    def upload_config(self, connection: NetworkDriver, config: str) -> bool:
        connection.load_replace_candidate(config=config)
        diff = connection.compare_config()
        if diff:
            self._log(
                'info', f'Configuration diff for device {connection.hostname}:\n{diff}'
            )
            connection.commit_config()
            return True
        else:
            self._log(
                'info', f'No configuration changes for device {connection.hostname}.'
            )
            connection.discard_config()
            return False

    def get_arp_entries(self, username, password, optional_args):
        interface_name = (
            self.source_device.interface.name if self.source_device.interface else None
        )
        if interface_name:
            message = (
                f'Running job on device {self.source_device.device.name} '
                f'with IP: {self.source_device.device.primary_ip4.address} using interface {interface_name}'
            )
        else:
            message = (
                f'Running job on device {self.source_device.device.name} '
                f'with IP: {self.source_device.device.primary_ip4}'
            )
        self._log('info', message)

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
        self._log(
            'success',
            f"Successfully connected to device '{self.source_device.device.name}'",
        )
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

        self._log(
            'info',
            f"Retrieved ARP entries for interface '{interface_name or 'all interfaces'}' and range '{self.source_device.ip_range or 'all addresses'}': {arp_entries}",
        )
        return arp_entries

    def connect_to_new_device(
        self, zeroday_username, zeroday_password, ip, optional_args
    ) -> tuple[NetworkDriver, FactsDict] | None:
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
            self._log(
                'success',
                f"Successfully connected to onboarded device with IP '{ip}' using driver '{self.source_device.onboarded_devices_vendor.slug.replace('juniper', 'junos').replace('cisco', 'ios')}'",
                ip_address=ip,
                serial_number=serial_number,
            )
            return onboarded_connection, facts

        except Exception as exc:  # noqa: BLE001
            self._log('error', f"Failed to connect to onboarded device with IP '{ip}' using driver '{driver_name}': {exc}", ip_address=ip)
            return None, None

    def create_primary_ip(
        self, device: Device, ip_address: str, connection: NetworkDriver, mac: str
    ) -> IPAddress:
        self._log('info', f"Creating primary IP '{ip_address}' for device '{device}'")
        mgmt_interface = Interface.objects.get(device=device, mgmt_only=True)
        MACAddress.objects.create(mac_address=mac, assigned_object_id=mgmt_interface.pk, assigned_object_type=ContentType.objects.get_for_model(Interface),)
        mgmt_ip = connection.get_interfaces_ip().get(mgmt_interface.name)
        ip = IPAddress.objects.create(
            address=f'{ip_address}/{mgmt_ip.get("ipv4", {}).get(ip_address, {}).get("prefix_length", "")}',
            assigned_object_id=mgmt_interface.pk,
            assigned_object_type=ContentType.objects.get_for_model(Interface),
        )
        self._log('info', f"Created primary IP '{ip_address}' for device '{device}'")
        return ip

    def create_new_device(
        self, connection: NetworkDriver, entry: ARPTableDict
    ) -> OnboardedDevice:
        facts = connection.get_facts() or {}
        self._log('info', f"Creating new device for entry '{entry}'")
        device = Device.objects.create(
            name=facts.get('serial_number'),
            role=DeviceRole.objects.get(name='ztp'),
            device_type=DeviceType.objects.get(part_number=facts.get('model') or ''),
            serial=facts.get('serial_number', ''),
            site=Site.objects.get(name='ztp'),
            tags=[Tag.objects.get(name='ztp')],
        )
        self._log('info', f"Created device '{device.pk}' for entry '{entry}'")
        self._log('info', f"Creating onboarded device for entry '{entry}'")
        onboarded_device = OnboardedDevice.objects.create(
            device=device,
            source_device=self.source_device,
        )
        self._log('info', f"Created onboarded device '{onboarded_device.pk}' for entry '{entry}'")
        self._log('info', f"Creating primary IP for device '{device.pk}' with entry '{entry}'")
        ip = self.create_primary_ip(
            device=device,
            ip_address=str(entry.get('ip', '')),
            connection=connection,
            mac=entry.get('mac', ''),
        )
        self._log('info', f"Created primary IP '{ip.pk}' for device '{device.pk}' with entry '{entry}'")
        try:
            self._log(
                'info',
                f'Setting primary and OOB IP for device {device}',
                ip_address=entry.get('ip', ''),
            )
            device.primary_ip4 = ip
            device.oob_ip = ip
            device.save()
            self._log(
                'info',
                f'Successfully set primary and OOB IP for device {device}',
                ip_address=entry.get('ip', ''),
            )
        except ValueError as e:
            self._log(
                'error', f'Error setting primary or OOB IP for device {device}: {e}'
            )
        return onboarded_device

    def run(self):
        username = get_plugin_config('netbox_ztp', 'username')
        password = get_plugin_config('netbox_ztp', 'password')
        zeroday_username = get_plugin_config('netbox_ztp', 'zeroday_username')
        zeroday_password = get_plugin_config('netbox_ztp', 'zeroday_password')
        optional_args = get_plugin_config('netbox_ztp', 'optional_args') or {}

        if not username or not password:
            self._log(
                'error', 'Missing username or password for ZTP plugin configuration'
            )
            return
        if not zeroday_username or not zeroday_password:
            self._log(
                'error',
                'Missing zeroday username or password for ZTP plugin configuration',
            )
            return

        arp_entries = self.get_arp_entries(username, password, optional_args)

        for entry in arp_entries:
            try:
                ip_value = str(entry.get('ip', ''))
                if not ip_value:
                    continue

                mac_object = MACAddress.objects.filter(
                    mac_address=entry.get('mac')
                ).first()
                onboarded_device = None
                connection = None
                facts = {}
                if mac_object and mac_object.assigned_object:
                    onboarded_device = (
                        mac_object.assigned_object.device.ztp_onboarded_device
                    )
                    self._log(
                        'info',
                        f'Found onboarded device for MAC {entry.get("mac")}',
                        ip_address=ip_value,
                    )

                if not onboarded_device:
                    self._log(
                        'info',
                        f'No onboarded device found for MAC {entry.get("mac")}',
                        ip_address=ip_value,
                    )
                    connection, facts = self.connect_to_new_device(
                        zeroday_username, zeroday_password, ip_value, optional_args
                    )
                    if not connection:
                        continue
                    onboarded_device = self.create_new_device(connection, entry)

                if onboarded_device.status == 'new' and self.update_needed(
                    re.findall(r'\d+.\d+.\d+', facts.get('os_version', ''))[0],
                    onboarded_device,
                ):
                    onboarded_device.status = 'needs_update'
                    onboarded_device.save()
                    self._log(
                        'info',
                        f'Update needed for device {onboarded_device.device.name}',
                        ip_address=ip_value,
                        serial_number=onboarded_device.device.serial,
                    )
                    self.update_device(connection, onboarded_device)
                    onboarded_device.status = 'updated'
                    onboarded_device.save()
                elif onboarded_device.status == "new" and not self.update_needed(
                    re.findall(r'\d+.\d+.\d+', facts.get('os_version', ''))[0],
                    onboarded_device,
                ):
                    onboarded_device.status = 'updated'
                    onboarded_device.save()

                if not connection:
                    continue
            except Exception as e:
                if facts:
                    Device.objects.get(serial=facts.get('serial_number')).delete()
                self._log(
                    'error',
                    f'Error processing ARP entry {entry}: {e}',
                    ip_address=ip_value,
                )
