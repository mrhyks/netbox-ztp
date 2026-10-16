from typing import ClassVar

from django import forms
from django.utils.translation import gettext as _

from dcim.models import Device
from netbox.forms import PrimaryModelForm
from netbox_ztp.models import SoftwareAssignment
from utilities.forms.fields import DynamicModelChoiceField


class SoftwareAssignmentForm(PrimaryModelForm):
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        label=_('Device'),
    )
    enabled = forms.BooleanField(label=_('Enabled'))
    scan_interval = forms.IntegerField(label=_('Scan Interval'))

    class Meta:
        model = SoftwareAssignment
        fields: ClassVar[list[str]] = ['device_types', 'checksum', 'version', 'description']
    