
from netbox.object_actions import BulkDelete, BulkExport
from netbox.views.generic import (
    BulkDeleteView,
    ObjectEditView,
    ObjectListView,
)
from netbox_ztp.models import ZTPLog
from netbox_ztp.tables import ZTPLogTable
from utilities.views import register_model_view

__all__ = [
    'ZTPLogBulkDeleteView',
    'ZTPLogBulkExportView',
    'ZTPLogListView',
]


@register_model_view(ZTPLog, name='list', path='', detail=False)
class ZTPLogListView(ObjectListView):
    queryset = ZTPLog.objects.all()
    table = ZTPLogTable
    actions = (BulkDelete, BulkExport)


@register_model_view(ZTPLog, name='bulk_delete', detail=False)
class ZTPLogBulkDeleteView(BulkDeleteView):
    queryset = ZTPLog.objects.all()


@register_model_view(ZTPLog, name='bulk_export',  detail=False)
class ZTPLogBulkExportView(BulkExport):
    queryset = ZTPLog.objects.all()

@register_model_view(ZTPLog, name='delete')
class ZTPLogEditView(ObjectEditView):
    queryset = ZTPLog.objects.all()
