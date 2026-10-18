from typing import ClassVar

from django.utils.translation import gettext as _

from dcim.models import Device, Interface, Manufacturer
from ipam.models import IPRange
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
    ip_range = CSVModelChoiceField(
        queryset=IPRange.objects.all(),
        required=False,
        label=_('IP Range'),
    )
    onboarded_devices_vendor = CSVModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=True,
        label=_('Onboarded Device Vendor'),
    )

    class Meta:
        model = SourceDevice
        fields: ClassVar[list[str]] = ['device', 'interface', 'ip_range', 'onboarded_devices_vendor', 'enabled', 'scan_interval']