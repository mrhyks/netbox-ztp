from typing import ClassVar

import django_tables2 as tables

from netbox.tables import NetBoxTable, columns
from netbox_ztp.models import OnboardedDevice, SoftwareAssignment, SourceDevice, ZTPLog


class SourceDeviceTable(NetBoxTable):
    device = tables.Column(accessor='device__name', verbose_name='Device', linkify=True)
    interface = tables.Column(accessor='interface__name', verbose_name='Interface', linkify=True)
    ip_range = tables.Column(verbose_name='IP Range')
    onboarded_devices_vendor = tables.Column(accessor='onboarded_devices_vendor__name', verbose_name='Onboarded Device Vendor')
    enabled = tables.BooleanColumn(verbose_name='Enabled')
    last_scan = tables.DateTimeColumn(verbose_name='Last scan')
    scan_interval = tables.Column(verbose_name='Scan interval')

    class Meta:
        model = SourceDevice
        fields = ('device', 'interface', 'ip_range', 'onboarded_devices_vendor', 'enabled', 'last_scan', 'scan_interval')
        attrs: ClassVar[dict[str, str]] = {'class': 'table table-striped table-hover'}


class OnboardedDeviceTable(NetBoxTable):
    serial_number = tables.Column(verbose_name='Serial')
    ip_address = tables.Column(verbose_name='IP')
    mac_address = tables.Column(verbose_name='MAC')
    platform = tables.Column(verbose_name='Platform')
    status = tables.Column(verbose_name='Status')

    class Meta:
        model = OnboardedDevice
        fields = ('serial_number', 'ip_address', 'mac_address', 'platform', 'status')
        attrs: ClassVar[dict[str, str]] = {'class': 'table table-striped table-hover'}


class ZTPLogTable(NetBoxTable):
    time = tables.DateTimeColumn(verbose_name='Time')
    level = tables.Column(verbose_name='Level')
    serial_number = tables.Column(verbose_name='Serial')
    ip_address = tables.Column(verbose_name='IP')
    message = tables.Column(verbose_name='Message')
    actions = columns.ActionsColumn(
        actions=('delete',)
    )

    class Meta:
        model = ZTPLog
        fields = ('time', 'level', 'serial_number', 'ip_address', 'message')
        attrs: ClassVar[dict[str, str]] = {'class': 'table table-striped table-hover'}

class SoftwareAssignmentTable(NetBoxTable):
    device_types = tables.Column(verbose_name='Device Types')
    checksum = tables.Column(verbose_name='Checksum')
    version = tables.Column(verbose_name='Version')
    description = tables.Column(verbose_name='Description')

    class Meta:
        model = SoftwareAssignment
        fields = ('device_types', 'checksum', 'version', 'description')
        attrs: ClassVar[dict[str, str]] = {'class': 'table table-striped table-hover'}