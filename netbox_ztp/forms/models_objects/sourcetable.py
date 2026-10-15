from typing import ClassVar

from django import forms
from django.utils.translation import gettext as _

from dcim.models import Device
from netbox.forms import PrimaryModelForm
from netbox_ztp.models import SourceDevice
from utilities.forms.fields import DynamicModelChoiceField


class SourceDeviceForm(PrimaryModelForm):
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        label=_('Device'),
    )
    enabled = forms.BooleanField(label=_('Enabled'))
    scan_interval = forms.IntegerField(label=_('Scan Interval'))

    class Meta:
        model = SourceDevice
        fields: ClassVar[list[str]] = ['device', 'enabled', 'scan_interval']
    