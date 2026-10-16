
from netbox.object_actions import BulkDelete, BulkExport
from netbox.views.generic import (
    BulkDeleteView,
    ObjectDeleteView,
    ObjectListView,
    ObjectView,
)
from netbox_ztp.filters import (
    OnboardedDeviceFilterForm,
    OnboardedDeviceFilterSet,
)
from netbox_ztp.models import OnboardedDevice
from netbox_ztp.tables import OnboardedDeviceTable
from utilities.views import register_model_view

__all__ = [
    'OnboardedDeviceBulkDeleteView',
    'OnboardedDeviceDeleteView',
    'OnboardedDeviceListView',
    'OnboardedDeviceView',
    ]

@register_model_view(OnboardedDevice, name='list', path='', detail=False)
class OnboardedDeviceListView(ObjectListView):
    queryset = OnboardedDevice.objects.all()
    filterset = OnboardedDeviceFilterSet
    filterset_form = OnboardedDeviceFilterForm
    table = OnboardedDeviceTable
    actions = (BulkDelete, BulkExport)


@register_model_view(OnboardedDevice)
class OnboardedDeviceView(ObjectView):
    queryset = OnboardedDevice.objects.all()
    template_name = 'generic/object.html'


@register_model_view(OnboardedDevice, name='delete')
class OnboardedDeviceDeleteView(ObjectDeleteView):
    queryset = OnboardedDevice.objects.all()

@register_model_view(OnboardedDevice, name='bulk_delete', detail=False)
class OnboardedDeviceBulkDeleteView(BulkDeleteView):
    queryset = OnboardedDevice.objects.all()
    filterset = OnboardedDeviceFilterSet
    table = OnboardedDeviceTable