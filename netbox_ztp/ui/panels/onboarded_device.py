from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels

__all__ = ['OnboardedDevicePanel']

class OnboardedDevicePanel(panels.ObjectAttributesPanel):
    device = attrs.RelatedObjectAttr('device', label=_("Device"), linkify=True)
    source_device = attrs.RelatedObjectAttr('source_device', label=_("Source Device"), linkify=True)
    ip_address = attrs.TextAttr('ip_address', label=_("IP Address"))
    mac_address = attrs.TextAttr('mac_address', label=_("MAC Address"))