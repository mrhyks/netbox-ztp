from typing import ClassVar

from netbox.forms import PrimaryModelForm
from netbox_ztp.models import SoftwareAssignment


class SoftwareAssignmentForm(PrimaryModelForm):

    class Meta:
        model = SoftwareAssignment
        fields: ClassVar[list[str]] = ['device_types', 'checksum', 'version', 'file_path', 'description']
    