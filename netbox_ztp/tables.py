from typing import ClassVar

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import NetBoxTable, columns
from netbox_ztp.models import OnboardedDevice, SoftwareAssignment, SourceDevice, ZTPLog


class SourceDeviceTable(NetBoxTable):
    device = tables.Column(
        accessor='device__name', verbose_name=_('Device'), linkify=True
    )
    interface = tables.Column(
        accessor='interface__name', verbose_name=_('Interface'), linkify=True
    )
    onboarded_devices_vendor = tables.Column(
        accessor='onboarded_devices_vendor__name',
        verbose_name=_('Onboarded Device Vendor'),
    )
    enabled = tables.BooleanColumn(verbose_name=_('Enabled'))
    last_scan = tables.DateTimeColumn(verbose_name=_('Last scan'))
    scan_interval = tables.Column(verbose_name=_('Scan interval'))

    class Meta:
        model = SourceDevice
        fields = (
            'device',
            'interface',
            'onboarded_devices_vendor',
            'enabled',
            'last_scan',
            'scan_interval',
        )
        attrs: ClassVar[dict[str, str]] = {'class': 'table table-striped table-hover'}


class OnboardedDeviceTable(NetBoxTable):
    device = tables.Column(
        accessor='device__name', verbose_name=_('Device'), linkify=True
    )
    source_device = tables.Column(
        accessor='source_device__device__name',
        verbose_name=_('Source Device'),
        linkify=True,
    )
    status = tables.Column(verbose_name=_('Status'))
    actions = columns.ActionsColumn(actions=('delete',))

    class Meta:
        model = OnboardedDevice
        fields = ('device', 'source_device', 'status', 'last_seen', 'created')
        attrs: ClassVar[dict[str, str]] = {'class': 'table table-striped table-hover'}


class ZTPLogTable(NetBoxTable):
    time = tables.DateTimeColumn(verbose_name=_('Time'))
    level = tables.Column(verbose_name=_('Level'))
    device = tables.Column(
        accessor='device__name',
        verbose_name=_('Device'),
        linkify=lambda record: record.device.get_absolute_url() if record.device else None, # type: ignore
    )
    ip_address = tables.Column(
        accessor='device__primary_ip4', verbose_name=_('Address'), linkify=True
    )
    message = tables.Column(verbose_name=_('Message'))
    actions = columns.ActionsColumn(actions=())

    class Meta:
        model = ZTPLog
        fields = ('time', 'level', 'device', 'ip_address', 'message')
        attrs: ClassVar[dict[str, str]] = {'class': 'table table-striped table-hover'}


class SoftwareAssignmentTable(NetBoxTable):
    device_types = tables.ManyToManyColumn(
        accessor='device_types', verbose_name=_('Device Types'), linkify_item=True
    )
    checksum = tables.Column(verbose_name=_('Checksum'))
    version = tables.Column(verbose_name=_('Version'))
    file_path = tables.Column(verbose_name=_('File Path'))
    description = tables.Column(verbose_name=_('Description'))

    class Meta:
        model = SoftwareAssignment
        fields = ('device_types', 'checksum', 'version', 'file_path', 'description')
        attrs: ClassVar[dict[str, str]] = {'class': 'table table-striped table-hover'}
