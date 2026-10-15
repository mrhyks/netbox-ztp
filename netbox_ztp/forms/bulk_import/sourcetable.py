from django.utils.translation import gettext as _

from dcim.models import Device
from netbox.forms import PrimaryModelForm
from netbox_ztp.models import SourceDevice
from utilities.forms.fields import CSVModelChoiceField


class SourceDeviceImportForm(PrimaryModelForm):
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        required=True,
        label=_("Device"),
    )

    class Meta:
        model = SourceDevice
        fields = ["device", "enabled", "scan_interval"]