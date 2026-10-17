from typing import ClassVar

from django import forms
from django.utils.translation import gettext as _

from dcim.models import Device, Interface
from ipam.models import IPRange
from netbox.forms import PrimaryModelForm
from netbox_ztp.models import SourceDevice
from utilities.forms.fields import DynamicModelChoiceField


class SourceDeviceForm(PrimaryModelForm):
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        label=_('Device'),
    )
    interface = DynamicModelChoiceField(
        queryset=Interface.objects.none(),
        required=False,
        selector=True,
        label=_('Interface'),
        help_text=_('Optional. Restrict ARP collection to this interface on the selected device.'),
        query_params={
            'device_id': '$device',
        },
    )
    ip_range = DynamicModelChoiceField(
        queryset=IPRange.objects.all(),
        required=False,
        label=_('IP Range'),
    )
    enabled = forms.BooleanField(label=_('Enabled'), required=False)
    scan_interval = forms.IntegerField(label=_('Scan Interval'), min_value=1, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.device_id:
            device_id = self.instance.device_id
        elif self.data and self.data.get('device'):
            device_id = self.data.get('device')
        else:
            device_id = None

        if device_id:
            self.fields['interface'].queryset = Interface.objects.filter(device_id=device_id)
        else:
            self.fields['interface'].queryset = Interface.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        selected_device = cleaned_data.get('device')
        selected_interface = cleaned_data.get('interface')
        if selected_interface and selected_device and selected_interface.device_id != selected_device.pk:
            raise forms.ValidationError(_('Selected interface must belong to the selected device.'))
        return cleaned_data

    class Meta:
        model = SourceDevice
        fields: ClassVar[list[str]] = ['device', 'interface', 'ip_range', 'enabled', 'scan_interval']
