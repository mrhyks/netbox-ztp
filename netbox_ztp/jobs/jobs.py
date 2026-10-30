import json
import re
from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from napalm import get_network_driver
from napalm.base.base import NetworkDriver
from netmiko import BaseConnection, ConnectHandler, file_transfer

from dcim.models import Device, DeviceRole, DeviceType, Interface, MACAddress, Site
from extras.models import Tag
from ipam.models import IPAddress
from netbox.plugins import get_plugin_config
from netbox_ztp.models import OnboardedDevice, SoftwareAssignment, SourceDevice, ZTPLog


def transfer_progress(filename, size, sent):
    if size:
        percent = (sent / size) * 100
        print(
            f'\rTransferring {filename!s}: {percent:6.2f}% ({sent}/{size} bytes)',
            end='',
            flush=True,
        )
        if sent >= size:
            print()


class OnboardDevices:
    def __init__(self, source_device: SourceDevice):
        self.source_device = source_device

    def _log(self, level, message, device: Device = None):
        ZTPLog.objects.create(
            source_device=self.source_device,
            level=level,
            device=device,
            message=message,
        )
        print(message)

    def _normalize_mac(self, mac: str) -> str:
        value = re.sub(r'[^0-9A-Fa-f]', '', str(mac or '')).lower()
        if len(value) == 14 and value.startswith('01'):
            value = value[2:]
        if len(value) != 12:
            return str(mac or '').strip().lower()
        return ':'.join(value[i : i + 2] for i in range(0, 12, 2))

    def _extract_cisco_dhcp_leases(self, output: str) -> list[dict]:
        leases = []
        for line in output.splitlines():
            line = line.strip()
            if not line or line.lower().startswith('ip address'):
                continue
            match = re.match(r'^(\d+\.\d+\.\d+\.\d+)\s+([0-9A-Fa-f\.:-]+)', line)
            if not match:
                continue
            ip_value = match.group(1)
            raw_mac = match.group(2)
            leases.append(
                {
                    'ip': ip_value,
                    'mac': self._normalize_mac(raw_mac),
                    'interface': None,
                    'source': 'dhcp',
                }
            )
        return leases

    def _extract_juniper_dhcp_leases(self, output: str) -> list[dict]:
        leases = []
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            match = re.search(
                r'(\d+\.\d+\.\d+\.\d+).*?([0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5})',
                line,
            )
            if not match:
                continue
            ip_value = match.group(1)
            mac_value = self._normalize_mac(match.group(2))
            interface_match = re.search(
                r'(ge-|xe-|et-|ae-|irb\.|vlan\.|reth)\S*$', line
            )
            interface_name = interface_match.group(0) if interface_match else None
            leases.append(
                {
                    'ip': ip_value,
                    'mac': mac_value,
                    'interface': interface_name,
                    'source': 'dhcp',
                }
            )
        return leases

    def get_dhcp_leases(self, username, password, optional_args):
        interface_name = (
            self.source_device.interface.name if self.source_device.interface else None
        )
        self._log(
            'info',
            f"Collecting DHCP leases from source device '{self.source_device.device.name}'",
            self.source_device.device,
        )

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

        leases = []
        try:
            if driver_name == 'ios':
                output = str(
                    connection.cli(['show ip dhcp binding']).get(
                        'show ip dhcp binding',
                        '',
                    )
                )
                leases = self._extract_cisco_dhcp_leases(output)
            elif driver_name == 'junos':
                command = f'show dhcp server binding {"interface " + interface_name if interface_name else ""} | no-more'
                output = str(connection.cli([command]).get(command, ''))
                leases = self._extract_juniper_dhcp_leases(output)
            else:
                self._log(
                    'warning',
                    f"DHCP lease collection is not implemented for driver '{driver_name}'",
                    self.source_device.device,
                )
        finally:
            connection.close()

        if interface_name:
            leases = [
                entry
                for entry in leases
                if str(entry.get('interface') or '').lower() == interface_name.lower()
            ]

        self._log(
            'info',
            f"Retrieved DHCP leases for interface '{interface_name or 'all interfaces'}': {json.dumps(leases, indent=2, sort_keys=True)}",
            self.source_device.device,
        )
        return leases

    def ensure_ztp_device_role(self):
        role = DeviceRole.objects.get_or_create(
            name='ztp',
            slug='ztp',
        )
        if role[1]:
            self._log('info', "Created device role 'ztp'")
        else:
            self._log('info', "Found device role 'ztp'")

    def ensure_ztp_site(self):
        _site, created = Site.objects.get_or_create(name='ztp')
        if created:
            self._log('info', "Created site 'ztp'")
        else:
            self._log('info', "Found site 'ztp'")

    def ensure_tag(self):
        _tag, created = Tag.objects.get_or_create(name='ztp')
        if created:
            self._log('info', "Created tag 'ztp'")
        else:
            self._log('info', "Found tag 'ztp'")

    def preflight_check(self):
        self._log('info', 'Running preflight check for ZTP plugin configuration')
        self.ensure_ztp_device_role()
        self.ensure_ztp_site()
        self.ensure_tag()

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

        self.preflight_check()

        dhcp_leases = self.get_dhcp_leases(username, password, optional_args)

        for entry in dhcp_leases:
            self._log('info', f'Processing DHCP lease entry: {entry}')
            address = str(entry.get('ip') or '').strip()
            mac_address = str(entry.get('mac') or '').strip()
            if self.source_device.onboarded_devices_vendor.slug == 'cisco':
                try:
                    CiscoOnboardedDeviceJob(
                        zeroday_username,
                        zeroday_password,
                        optional_args,
                        address,
                        mac_address,
                        'ios',
                        self.source_device,
                    ).onboard_device()
                except Exception as e:  # noqa: BLE001
                    self._log(
                        'error', f"Failed to onboard device at address '{address}': {e}"
                    )


class BaseOnboardedDeviceJob(OnboardDevices):
    """Base job class for onboarding a single device."""

    def __init__(
        self,
        username: str,
        password: str,
        optional_args: dict,
        address: str,
        mac_address: str,
        driver: str,
        source_device: SourceDevice,
    ):
        self.username = username
        self.password = password
        self.optional_args = optional_args
        self.address = address
        self.driver = driver
        self.mac_address = mac_address
        self.source_device = source_device
        self._napalm_connection: NetworkDriver = self.napalm_connect()
        self._netmiko_connection: BaseConnection = self.netmiko_connect()
        self.onboarded_device = self.ensure_device()
        self.assignment = SoftwareAssignment.objects.get(
            device_types=self.onboarded_device.device.device_type
        )
        self.onboarded_device.last_seen = datetime.now()
        self.onboarded_device.save()

    def napalm_connect(self) -> NetworkDriver:
        """Establish a NAPALM connection to the device."""
        driver = get_network_driver(self.driver)
        connection = driver(
            hostname=self.address,
            username=self.username,
            password=self.password,
            optional_args=self.optional_args,
            timeout=15,
        )
        connection.open()
        self._facts = connection.get_facts() or {}
        return connection

    def netmiko_connect(self) -> BaseConnection:
        """Establish a Netmiko connection to the device."""
        connection = ConnectHandler(
            device_type=self.driver.replace('ios', 'cisco_ios').replace(
                'junos', 'juniper_junos'
            ),
            host=self.address,
            username=self.username,
            password=self.password,
            **self.optional_args,
            timeout=15,
        )
        return connection

    def create_new_device(self) -> OnboardedDevice:

        self._log(
            'info',
            f"Creating new device for address '{self.address}'",
            self.onboarded_device.device,
        )
        device = Device.objects.create(
            name=self._facts.get('serial_number'),
            role=DeviceRole.objects.get(name='ztp'),
            device_type=DeviceType.objects.get(
                part_number=self._facts.get('model') or ''
            ),
            serial=self._facts.get('serial_number', ''),
            site=Site.objects.get(name='ztp'),
        )
        device.tags.add(Tag.objects.get(name='ztp'))
        device.save()
        self._log(
            'info',
            f"Created device '{device.pk}' for address '{self.address}'",
            self.onboarded_device.device,
        )

        self._log(
            'info',
            f"Creating onboarded device for address '{self.address}'",
            self.onboarded_device.device,
        )
        onboarded_device = OnboardedDevice.objects.create(
            device=device,
            source_device=self.source_device,
        )
        self._log(
            'info',
            f"Created onboarded device '{onboarded_device.pk}' for address '{self.address}'",
            self.onboarded_device.device,
        )

        self._log(
            'info',
            f"Creating primary IP for device '{device.pk}' with address '{self.address}'",
            self.onboarded_device.device,
        )
        ip = self.create_primary_ip(
            device=device,
            ip_address=str(self.address),
            connection=self._napalm_connection,
            mac=self.mac_address,
        )
        self._log(
            'info',
            f"Created primary IP '{ip.pk}' for device '{device.pk}' with address '{self.address}'",
            self.onboarded_device.device,
        )

        try:
            self._log(
                'info',
                f'Setting primary and OOB IP for device {device}',
                self.onboarded_device.device,
            )
            device.primary_ip4 = ip
            device.oob_ip = ip
            device.save()
            self._log(
                'info',
                f'Successfully set primary and OOB IP for device {device}',
                self.onboarded_device.device,
            )
        except ValueError as e:
            self._log(
                'error',
                f'Error setting primary or OOB IP for device {device}: {e}',
                self.onboarded_device.device,
            )
        return onboarded_device

    def ensure_device(self) -> OnboardedDevice:
        """Ensure the device exists and return the onboarded device."""
        try:
            return OnboardedDevice.objects.get(
                device__serial=self._facts.get('serial_number')
            )
        except OnboardedDevice.DoesNotExist:
            return self.create_new_device()

    def update_needed(self):
        version = re.findall(r'\d+.\d+.\d+', self._facts.get('os_version', ''))[0]
        if not self.onboarded_device.device.primary_ip4:
            return False
        self._log(
            'info',
            f'Checking if update is needed for device {self.onboarded_device.device.name}',
            self.onboarded_device.device,
        )
        self._log(
            'info',
            f'Found {"1" if self.assignment else "0"} software assignments for device {self.onboarded_device.device.name}',
            self.onboarded_device.device,
        )
        self._log(
            'info',
            f'Current software version for device {self.onboarded_device.device.name} is {version} and required is {self.assignment.version if self.assignment else "N/A"}',
            self.onboarded_device.device,
        )
        return bool(self.assignment and self.assignment.version != version)

    def upload_config(self, connection: NetworkDriver, config: str) -> bool:
        connection.load_replace_candidate(config=config)
        diff = connection.compare_config()
        if diff:
            self._log(
                'info',
                f'Configuration diff for device {connection.hostname}:\n{diff}',
                self.onboarded_device.device,
            )
            connection.commit_config()
            return True
        else:
            self._log(
                'info',
                f'No configuration changes for device {connection.hostname}.',
                self.onboarded_device.device,
            )
            connection.discard_config()
            return False

    def create_primary_ip(
        self, device: Device, ip_address: str, connection: NetworkDriver, mac: str
    ) -> IPAddress:
        self._log(
            'info',
            f"Creating primary IP '{ip_address}' for device '{device}'",
            self.onboarded_device.device,
        )
        mgmt_interface = Interface.objects.get(device=device, mgmt_only=True)
        MACAddress.objects.create(
            mac_address=mac,
            assigned_object_id=mgmt_interface.pk,
            assigned_object_type=ContentType.objects.get_for_model(Interface),
        )
        mgmt_ip = connection.get_interfaces_ip().get(mgmt_interface.name)
        ip = IPAddress.objects.create(
            address=f'{ip_address}/{mgmt_ip.get("ipv4", {}).get(ip_address, {}).get("prefix_length", "")}',
            assigned_object_id=mgmt_interface.pk,
            assigned_object_type=ContentType.objects.get_for_model(Interface),
        )
        self._log(
            'info',
            f"Created primary IP '{ip_address}' for device '{device}'",
            self.onboarded_device.device,
        )
        return ip


class CiscoOnboardedDeviceJob(BaseOnboardedDeviceJob):
    def ensure_scp_server(self) -> None:
        """Ensure the SCP server is enabled on the device."""
        try:
            output = self._netmiko_connection.send_command('show run | include scp')
            if not 'ip scp server enable' in output:
                self._netmiko_connection.config_mode()
                self._netmiko_connection.send_command('ip scp server enable')
                self._netmiko_connection.exit_config_mode()
        except Exception as e:  # noqa: BLE001
            self._log(
                'error',
                f'Failed to check SCP server on device {self._netmiko_connection.host}: {e}',
                self.onboarded_device.device,
            )

    def check_file_exists(self) -> bool:
        """Check if the file exists on the device."""
        try:
            output = self._netmiko_connection.send_command(
                f'dir flash: | include {self.assignment.file_path.split("/")[-1]}'
            )
            return self.assignment.file_path.split('/')[-1] in output
        except Exception as e:  # noqa: BLE001
            self._log(
                'error',
                f'Failed to check file existence on device {self._netmiko_connection.host}: {e}',
                self.onboarded_device.device,
            )
            return False

    def update_device(self) -> None:
        """Update the device version as needed."""
        try:
            self.ensure_scp_server()
            if not self.check_file_exists():
                file_transfer(
                    self._netmiko_connection,
                    source_file=self.assignment.file_path,
                    dest_file=self.assignment.file_path.split('/')[-1],
                    file_system='flash:',
                    direction='put',
                    overwrite_file=False,
                    progress=transfer_progress,
                )
                self._log(
                    'info',
                    f'Transferred file {self.assignment.file_path} to device {self.address}.',
                    self.onboarded_device.device,
                )
            else:
                self._log(
                    'info',
                    f'File {self.assignment.file_path} already exists on device {self.address}.',
                    self.onboarded_device.device,
                )
            self._netmiko_connection.send_command('write memory')
            self._log(
                'success',
                f'Wrote memory on device {self.address}.',
                self.onboarded_device.device,
            )
            self._netmiko_connection.send_command_timing(
                f'install add file flash:{self.assignment.file_path.split("/")[-1]} activate commit prompt-level none',
                cmd_verify=False,
                strip_prompt=False,
                strip_command=False,
            )

            self._log(
                'success',
                f'Device {self.address} updated with file {self.assignment.file_path.split("/")[-1]}, waiting for restart.',
                self.onboarded_device.device,
            )
            self._netmiko_connection.disconnect()
        except Exception as e:  # noqa: BLE001
            self._log(
                'error',
                f'Failed to update device {self._netmiko_connection.host}: {e}',
                self.onboarded_device.device,
            )

    def update_cleanup(self) -> None:
        """Clean up inactive packages on the device."""
        try:
            self._log(
                'info',
                f'Cleaning up inactive packages on device {self.address}.',
                self.onboarded_device.device,
            )
            remove_inactive_output = self._netmiko_connection.send_command_timing(
                'install remove inactive',
                cmd_verify=False,
                strip_prompt=False,
                strip_command=False,
            )
            remove_inactive_output_text = str(remove_inactive_output)
            if re.search(
                r'Do you want to remove the above files\?\s*\[y/n\]',
                remove_inactive_output_text,
                re.IGNORECASE,
            ):
                remove_inactive_output_text += str(
                    self._netmiko_connection.send_command_timing(
                        'y',
                        cmd_verify=False,
                        strip_prompt=False,
                        strip_command=False,
                    )
                )
            self._log(
                'success',
                f'Inactive package cleanup output for device {self.address}:\n{remove_inactive_output_text}',
                self.onboarded_device.device,
            )
        except Exception as e:  # noqa: BLE001
            self._log(
                'error',
                f'Failed to clean up inactive packages on device {self._netmiko_connection.host}: {e}',
                self.onboarded_device.device,
            )

    def onboard_device(self) -> None:
        """Onboard the device."""
        try:
            if self.onboarded_device.status == 'new' and self.update_needed():
                self.onboarded_device.status = 'needs_update'
                self.onboarded_device.save()
                self.update_device()
                self.onboarded_device.status = 'updating'
                self.onboarded_device.save()

            elif self.onboarded_device.status == 'new' and not self.update_needed():
                self.onboarded_device.status = 'updated'
                self.onboarded_device.save()

            elif (
                self.onboarded_device.status == 'needs_update' and self.update_needed()
            ):
                self.update_device()
                self.onboarded_device.status = 'updating'
                self.onboarded_device.save()

            elif (
                self.onboarded_device.status == 'needs_update'
                or self.onboarded_device.status == 'updating'
            ) and not self.update_needed():
                self.onboarded_device.status = 'updated'
                self.onboarded_device.save()
            else:
                self._log(
                    'success',
                    f'No update needed for device {self.address}',
                    self.onboarded_device.device,
                )

            self._netmiko_connection.disconnect()
            self._napalm_connection.close()

        except Exception as e:  # noqa: BLE001
            self._log(
                'error',
                f'Failed to onboard device {self.address}: {e}',
                self.onboarded_device.device,
            )
