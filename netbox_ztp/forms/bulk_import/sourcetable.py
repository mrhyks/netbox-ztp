from typing import ClassVar

from django.utils.translation import gettext as _

from dcim.models import Device, Interface
from netbox.forms import PrimaryModelForm
from netbox_ztp.models import SourceDevice
from utilities.forms.fields import CSVModelChoiceField


class SourceDeviceImportForm(PrimaryModelForm):
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        required=True,
        label=_('Device'),
    )
    interface = CSVModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label=_('Interface'),
    )

    class Meta:
        model = SourceDevice
        fields: ClassVar[list[str]] = ['device', 'interface', 'enabled', 'scan_interval']