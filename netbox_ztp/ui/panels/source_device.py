from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels

__all__ = ['SourceDevicePanel']

class SourceDevicePanel(panels.ObjectAttributesPanel):
    device = attrs.RelatedObjectAttr('device', label=_('Device'), linkify=True)
    interface = attrs.RelatedObjectAttr('interface', label=_('Interface'), linkify=True)
    ip_range = attrs.RelatedObjectAttr('ip_range', label=_('IP Range'), linkify=True)
    onboarded_devices_vendor = attrs.RelatedObjectAttr('onboarded_devices_vendor', label=_('Onboarded Device Vendor'), linkify=True)
    enabled = attrs.BooleanAttr('enabled', label=_('Enabled'))
    last_scan = attrs.DateTimeAttr('last_scan', label=_('Last Scan'))
    scan_interval = attrs.TextAttr('scan_interval', label=_('Scan Interval'))
