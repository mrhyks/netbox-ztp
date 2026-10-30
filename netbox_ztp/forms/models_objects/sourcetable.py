from typing import ClassVar

from django import forms
from django.utils.translation import gettext as _

from dcim.models import Device, Interface, Manufacturer
from netbox.forms import PrimaryModelForm
from netbox_ztp.models import SourceDevice
from utilities.forms.fields import DynamicModelChoiceField


class SourceDeviceForm(PrimaryModelForm):
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        label=_('Device'),
    )
    interface = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        selector=True,
        label=_('Interface'),
        help_text=_('Optional. Restrict ARP collection to this interface on the selected device.'),
        query_params={
            'device_id': '$device',
        },
    )
    onboarded_devices_vendor = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        label=_('Onboarded Device Vendor'),
        help_text=_('Required vendor used for onboarding discovered devices.'),
    )
    enabled = forms.BooleanField(label=_('Enabled'), required=False)
    scan_interval = forms.IntegerField(label=_('Scan Interval'), min_value=1, required=False)

    class Meta:
        model = SourceDevice
        fields: ClassVar[list[str]] = ['device', 'interface', 'onboarded_devices_vendor', 'enabled', 'scan_interval']
