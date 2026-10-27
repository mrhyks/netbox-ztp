from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels

__all__ = ['OnboardedDevicePanel']

class OnboardedDevicePanel(panels.ObjectAttributesPanel):
    device = attrs.RelatedObjectAttr('device', label=_("Device"), linkify=True)
    source_device = attrs.RelatedObjectAttr('source_device', label=_("Source Device"), linkify=True)
    status = attrs.RelatedObjectAttr('status', label=_("Status"))
    last_seen = attrs.RelatedObjectAttr('last_seen', label=_("Last Seen"))
    created = attrs.RelatedObjectAttr('created', label=_("Created"))