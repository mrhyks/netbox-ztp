
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
    SoftwareAssignmentFilterForm,
    SoftwareAssignmentFilterSet,
)
from netbox_ztp.forms import (
    SoftwareAssignmentForm,
    SoftwareAssignmentImportForm,
)
from netbox_ztp.models import SoftwareAssignment
from netbox_ztp.tables import SoftwareAssignmentTable
from netbox_ztp.ui import SoftwareAssignmentPanel
from utilities.views import register_model_view

__all__ = [
    'SoftwareAssignmentBulkDeleteView',
    'SoftwareAssignmentBulkEditView',
    'SoftwareAssignmentBulkImportView',
    'SoftwareAssignmentDeleteView',
    'SoftwareAssignmentEditView',
    'SoftwareAssignmentListView',
    'SoftwareAssignmentView',
]


@register_model_view(SoftwareAssignment, name='list', path='', detail=False)
class SoftwareAssignmentListView(ObjectListView):
    queryset = SoftwareAssignment.objects.all()
    filterset = SoftwareAssignmentFilterSet
    filterset_form = SoftwareAssignmentFilterForm
    table = SoftwareAssignmentTable


@register_model_view(SoftwareAssignment)
class SoftwareAssignmentView(ObjectView):
    queryset = SoftwareAssignment.objects.all()
    template_name = 'generic/object.html'
    layout = layout.SimpleLayout(
        left_panels=[
            SoftwareAssignmentPanel(),
        ],
        right_panels=[
            panels.CommentsPanel(),
            panels.RelatedObjectsPanel(),
        ],
    )


@register_model_view(SoftwareAssignment, name='delete')
class SoftwareAssignmentDeleteView(ObjectDeleteView):
    queryset = SoftwareAssignment.objects.all()

@register_model_view(SoftwareAssignment, name='add', detail=False)
@register_model_view(SoftwareAssignment, name='edit')
class SoftwareAssignmentEditView(ObjectEditView):
    queryset = SoftwareAssignment.objects.all()
    form = SoftwareAssignmentForm


@register_model_view(SoftwareAssignment, name='bulk_delete', detail = False)
class SoftwareAssignmentBulkDeleteView(BulkDeleteView):
    queryset = SoftwareAssignment.objects.all()
    filterset = SoftwareAssignmentFilterSet
    table = SoftwareAssignmentTable
    
@register_model_view(SoftwareAssignment, name='bulk_edit', detail = False)
class SoftwareAssignmentBulkEditView(BulkEditView):
    queryset = SoftwareAssignment.objects.all()
    filterset = SoftwareAssignmentFilterSet
    table = SoftwareAssignmentTable
    
@register_model_view(SoftwareAssignment, name='bulk_import', detail = False)
class SoftwareAssignmentBulkImportView(BulkImportView):
    queryset = SoftwareAssignment.objects.all()
    model_form = SoftwareAssignmentImportForm

