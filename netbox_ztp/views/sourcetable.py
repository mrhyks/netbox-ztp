
from netbox.views.generic import (
    BulkDeleteView,
    BulkEditView,
    BulkImportView,
    ObjectEditView,
    ObjectDeleteView,
    ObjectListView,
    ObjectView,
)
from utilities.views import register_model_view
from netbox_ztp.forms import SourceDeviceForm, SourceDeviceImportForm
from netbox.ui import layout
from netbox_ztp.filters import (
    SourceDeviceFilterForm,
    SourceDeviceFilterSet,
)
from netbox_ztp.models import SourceDevice
from netbox_ztp.tables import SourceDeviceTable

__all__ = [
    "SourceDeviceBulkDeleteView",
    "SourceDeviceBulkEditView",
    "SourceDeviceDeleteView",
    "SourceDeviceListView",
    "SourceDeviceView",
]


@register_model_view(SourceDevice, name="list", path="", detail=False)
class SourceDeviceListView(ObjectListView):
    queryset = SourceDevice.objects.all()
    filterset = SourceDeviceFilterSet
    filterset_form = SourceDeviceFilterForm
    table = SourceDeviceTable


@register_model_view(SourceDevice, name="view")
class SourceDeviceView(ObjectView):
    queryset = SourceDevice.objects.all()
    template_name = "generic/object.html"


@register_model_view(SourceDevice, name="delete")
class SourceDeviceDeleteView(ObjectDeleteView):
    queryset = SourceDevice.objects.all()

@register_model_view(SourceDevice, name="add", detail=False)
@register_model_view(SourceDevice, name="edit")
class SourceDeviceEditView(ObjectEditView):
    queryset = SourceDevice.objects.all()
    form = SourceDeviceForm


@register_model_view(SourceDevice, name="bulk-delete")
class SourceDeviceBulkDeleteView(BulkDeleteView):
    queryset = SourceDevice.objects.all()
    filterset = SourceDeviceFilterSet
    table = SourceDeviceTable
    
@register_model_view(SourceDevice, name="bulk-edit")
class SourceDeviceBulkEditView(BulkEditView):
    queryset = SourceDevice.objects.all()
    filterset = SourceDeviceFilterSet
    table = SourceDeviceTable
    
@register_model_view(SourceDevice, name="bulk-import")
class SourceDeviceBulkImportView(BulkImportView):
    queryset = SourceDevice.objects.all()
    model_form = SourceDeviceImportForm
