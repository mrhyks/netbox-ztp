from django.urls import path

from netbox.views.generic import ObjectChangeLogView
from netbox_ztp.models import OnboardedDevice, SoftwareAssignment, SourceDevice
from netbox_ztp.views import (
    OnboardedDeviceBulkDeleteView,
    OnboardedDeviceDeleteView,
    OnboardedDeviceListView,
    OnboardedDeviceView,
    SourceDeviceBulkDeleteView,
    SourceDeviceBulkEditView,
    SourceDeviceBulkImportView,
    SourceDeviceDeleteView,
    SourceDeviceEditView,
    SourceDeviceListView,
    SourceDeviceView,
)
from netbox_ztp.views.software_assignment import SoftwareAssignmentListView

app_name = 'netbox_ztp'

urlpatterns = [
    path('source-devices/', SourceDeviceListView.as_view(), name='sourcedevice_list'),
    path('source-devices/add/', SourceDeviceEditView.as_view(), name='sourcedevice_add'),
    path('source-devices/bulk-delete/', SourceDeviceBulkDeleteView.as_view(), name='sourcedevice_bulk_delete'),
    path('source-devices/bulk-edit/', SourceDeviceBulkEditView.as_view(), name='sourcedevice_bulk_edit'),
    path('source-devices/bulk-import/', SourceDeviceBulkImportView.as_view(), name='sourcedevice_bulk_import'),
    path('source-devices/<int:pk>/', SourceDeviceView.as_view(), name='sourcedevice'),
    path('source-devices/<int:pk>/edit/', SourceDeviceEditView.as_view(), name='sourcedevice_edit'),
    path('source-devices/<int:pk>/delete/', SourceDeviceDeleteView.as_view(), name='sourcedevice_delete'),
    path(
        'source-devices/<int:pk>/changelog/',
        ObjectChangeLogView.as_view(),
        name='sourcedevice_changelog',
        kwargs={'model': SourceDevice},
    ),
    path('onboarded-devices/', OnboardedDeviceListView.as_view(), name='onboarded_device_list'),
    path('onboarded-devices/bulk-delete/', OnboardedDeviceBulkDeleteView.as_view(), name='onboarded_device_bulk_delete'),
    path('onboarded-devices/<int:pk>/', OnboardedDeviceView.as_view(), name='onboarded_device'),
    path('onboarded-devices/<int:pk>/delete/', OnboardedDeviceDeleteView.as_view(), name='onboarded_device_delete'),
    path(
        'onboarded-devices/<int:pk>/changelog/',
        ObjectChangeLogView.as_view(),
        name='onboarded_device_changelog',
        kwargs={'model': OnboardedDevice},
    ),
    path('software-assignments/', SoftwareAssignmentListView.as_view(), name='software_assignment_list'),
    path('software-assignments/<int:pk>/', SoftwareAssignmentListView.as_view(), name='software_assignment'),
    path('software-assignments/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='software_assignment_changelog', kwargs={'model': SoftwareAssignment}),
    path('software-assignments/<int:pk>/edit/', SoftwareAssignmentListView.as_view(), name='software_assignment_edit'),
    path('software-assignments/<int:pk>/delete/', SoftwareAssignmentListView.as_view(), name='software_assignment_delete'),
    path('software-assignments/add/', SoftwareAssignmentListView.as_view(), name='software_assignment_add'),
    
]
