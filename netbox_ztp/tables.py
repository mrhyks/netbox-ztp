import django_tables2 as tables

from .models import OnboardedDevice, SourceDevice, ZTPLog


class SourceDeviceTable(tables.Table):
    device = tables.Column(accessor="device__name", verbose_name="Device")
    enabled = tables.BooleanColumn(verbose_name="Enabled")
    last_scan = tables.DateTimeColumn(verbose_name="Last scan")
    scan_interval = tables.Column(verbose_name="Scan interval")

    class Meta:
        model = SourceDevice
        fields = ("device", "enabled", "last_scan", "scan_interval")
        attrs = {"class": "table table-striped table-hover"}


class OnboardedDeviceTable(tables.Table):
    serial_number = tables.Column(verbose_name="Serial")
    ip_address = tables.Column(verbose_name="IP")
    mac_address = tables.Column(verbose_name="MAC")
    platform = tables.Column(verbose_name="Platform")
    status = tables.Column(verbose_name="Status")

    class Meta:
        model = OnboardedDevice
        fields = ("serial_number", "ip_address", "mac_address", "platform", "status")
        attrs = {"class": "table table-striped table-hover"}


class ZTPLogTable(tables.Table):
    time = tables.DateTimeColumn(verbose_name="Time")
    level = tables.Column(verbose_name="Level")
    serial_number = tables.Column(verbose_name="Serial")
    ip_address = tables.Column(verbose_name="IP")
    message = tables.Column(verbose_name="Message")

    class Meta:
        model = ZTPLog
        fields = ("time", "level", "serial_number", "ip_address", "message")
        attrs = {"class": "table table-striped table-hover"}
