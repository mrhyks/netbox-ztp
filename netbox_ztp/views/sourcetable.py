from typing import ClassVar

from django.contrib import messages
from django.shortcuts import redirect
from django.views import View

from netbox.object_actions import DeleteObject, EditObject
from netbox.ui import layout, panels
from netbox.views.generic import (
    BulkDeleteView,
    BulkEditView,
    BulkImportView,
    ObjectDeleteView,
    ObjectEditView,
    ObjectListView,
    ObjectView,
)
from netbox_ztp.filters import (
    SourceDeviceFilterForm,
    SourceDeviceFilterSet,
)
from netbox_ztp.forms import SourceDeviceForm, SourceDeviceImportForm
from netbox_ztp.jobs.actions import IngestDevices
from netbox_ztp.jobs.actions import OnboardDevices as OnboardDeviceAction
from netbox_ztp.jobs.jobs import OnboardDevices as OnboardDeviceScript
from netbox_ztp.models import SourceDevice
from netbox_ztp.tables import SourceDeviceTable
from netbox_ztp.ui import SourceDevicePanel
from utilities.views import register_model_view

__all__ = [
    'SourceDeviceBulkDeleteView',
    'SourceDeviceBulkEditView',
    'SourceDeviceBulkImportView',
    'SourceDeviceDeleteView',
    'SourceDeviceEditView',
    'SourceDeviceListView',
    'SourceDeviceView',
]


@register_model_view(SourceDevice, name='list', path='', detail=False)
class SourceDeviceListView(ObjectListView):
    queryset = SourceDevice.objects.all()
    filterset = SourceDeviceFilterSet
    filterset_form = SourceDeviceFilterForm
    table = SourceDeviceTable


@register_model_view(SourceDevice)
class SourceDeviceView(ObjectView):
    queryset = SourceDevice.objects.all()
    template_name = 'generic/object.html'
    layout = layout.SimpleLayout(
        left_panels=[
            SourceDevicePanel(),
        ],
        right_panels=[
            panels.CommentsPanel(),
            panels.RelatedObjectsPanel(),
        ],
    )
    actions: ClassVar[list[object]] = [EditObject, DeleteObject, IngestDevices, OnboardDeviceAction]


@register_model_view(SourceDevice, name='onboard')
class SourceDeviceOnboardView(View):
    def get(self, request, pk):
        obj = SourceDevice.objects.get(pk=pk)
        OnboardDeviceScript(obj).run()
        messages.success(request, f'Onboard workflow launched for {obj}')
        return redirect(obj.get_absolute_url())


@register_model_view(SourceDevice, name='delete')
class SourceDeviceDeleteView(ObjectDeleteView):
    queryset = SourceDevice.objects.all()

@register_model_view(SourceDevice, name='add', detail=False)
@register_model_view(SourceDevice, name='edit')
class SourceDeviceEditView(ObjectEditView):
    queryset = SourceDevice.objects.all()
    form = SourceDeviceForm


@register_model_view(SourceDevice, name='bulk_delete', detail = False)
class SourceDeviceBulkDeleteView(BulkDeleteView):
    queryset = SourceDevice.objects.all()
    filterset = SourceDeviceFilterSet
    table = SourceDeviceTable
    
@register_model_view(SourceDevice, name='bulk_edit', detail = False)
class SourceDeviceBulkEditView(BulkEditView):
    queryset = SourceDevice.objects.all()
    filterset = SourceDeviceFilterSet
    table = SourceDeviceTable
    
@register_model_view(SourceDevice, name='bulk_import', detail = False)
class SourceDeviceBulkImportView(BulkImportView):
    queryset = SourceDevice.objects.all()
    model_form = SourceDeviceImportForm

