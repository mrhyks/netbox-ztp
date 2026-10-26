from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels


class SoftwareAssignmentPanel(panels.ObjectAttributesPanel):
    device_types = attrs.TextAttr('device_types', label=_("Device Types"))
    checksum = attrs.TextAttr('checksum', label=_("Checksum"))
    version = attrs.TextAttr('version', label=_("Version"))
    file_path = attrs.TextAttr('file_path', label=_("File Path"))
    description = attrs.TextAttr('description', label=_("Description"))