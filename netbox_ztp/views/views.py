from django.utils.translation import gettext_lazy as _

from netbox.views.generic import (
    BulkDeleteView,
    BulkEditView,
    ObjectDeleteView,
    ObjectListView,
    ObjectView,
)
from utilities.views import register_model_view

from netbox_ztp.filters import OnboardedDeviceFilterSet, SourceDeviceFilterForm, SourceDeviceFilterSet
from netbox_ztp.models import OnboardedDevice, SourceDevice, ZTPLog
from netbox_ztp.tables import OnboardedDeviceTable, SourceDeviceTable, ZTPLogTable

__all__ = [
    "SourceDeviceListView",
    "SourceDeviceView",
    "SourceDeviceDeleteView",
    "SourceDeviceBulkEditView",
    "SourceDeviceBulkDeleteView",
    "OnboardedDeviceListView",
    "OnboardedDeviceView",
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
    template_name = "netbox_ztp/source_device.html"

    def get_extra_context(self, request, instance):
        return {
            "device": instance.device,
            "last_scan": instance.last_scan,
            "scan_interval": instance.scan_interval,
        }


@register_model_view(SourceDevice, name="delete")
class SourceDeviceDeleteView(ObjectDeleteView):
    queryset = SourceDevice.objects.all()
    template_name = "netbox_ztp/source_device_delete.html"


@register_model_view(SourceDevice, name="edit")
class SourceDeviceBulkEditView(BulkEditView):
    queryset = SourceDevice.objects.all()
    filterset = SourceDeviceFilterSet
    table = SourceDeviceTable


@register_model_view(SourceDevice, name="delete", path="bulk-delete")
class SourceDeviceBulkDeleteView(BulkDeleteView):
    queryset = SourceDevice.objects.all()
    filterset = SourceDeviceFilterSet
    table = SourceDeviceTable


@register_model_view(OnboardedDevice, name="list", path="", detail=False)
class OnboardedDeviceListView(ObjectListView):
    queryset = OnboardedDevice.objects.all()
    filterset = OnboardedDeviceFilterSet
    table = OnboardedDeviceTable


@register_model_view(OnboardedDevice, name="view")
class OnboardedDeviceView(ObjectView):
    queryset = OnboardedDevice.objects.all()
    template_name = "netbox_ztp/onboarded_device.html"

    def get_extra_context(self, request, instance):
        return {
            "source_device": instance.source_device,
            "serial_number": instance.serial_number,
            "status": instance.status,
        }


@register_model_view(ZTPLog, name="list", path="", detail=False)
class ZTPLogListView(ObjectListView):
    queryset = ZTPLog.objects.all()
    table = ZTPLogTable
