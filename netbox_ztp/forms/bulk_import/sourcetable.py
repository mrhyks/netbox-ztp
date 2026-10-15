from typing import ClassVar

from django.utils.translation import gettext as _

from dcim.models import Device
from netbox.forms import PrimaryModelForm
from netbox_ztp.models import SourceDevice
from utilities.forms.fields import CSVModelChoiceField


class SourceDeviceImportForm(PrimaryModelForm):
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        required=True,
        label=_('Device'),
    )

    class Meta:
        model = SourceDevice
        fields: ClassVar[list[str]] = ['device', 'enabled', 'scan_interval']