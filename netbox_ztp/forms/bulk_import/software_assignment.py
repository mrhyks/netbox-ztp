from typing import ClassVar

from django.utils.translation import gettext as _

from dcim.models import Device
from netbox.forms import PrimaryModelForm
from netbox_ztp.models import SoftwareAssignment
from utilities.forms.fields import CSVModelChoiceField


class SoftwareAssignmentImportForm(PrimaryModelForm):
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        required=True,
        label=_('Device'),
    )

    class Meta:
        model = SoftwareAssignment
        fields: ClassVar[list[str]] = ['device_types', 'checksum', 'version', 'description']