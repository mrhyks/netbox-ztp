from rest_framework.viewsets import ModelViewSet

from netbox_ztp.models import OnboardedDevice, SoftwareAssignment, SourceDevice, ZTPLog

from .serializers import (
    OnboardedDeviceSerializer,
    SoftwareAssignmentSerializer,
    SourceDeviceSerializer,
    ZTPLogSerializer,
)


class SourceDeviceViewSet(ModelViewSet):
    queryset = SourceDevice.objects.all()
    serializer_class = SourceDeviceSerializer


class OnboardedDeviceViewSet(ModelViewSet):
    queryset = OnboardedDevice.objects.all()
    serializer_class = OnboardedDeviceSerializer


class ZTPLogViewSet(ModelViewSet):
    queryset = ZTPLog.objects.all()
    serializer_class = ZTPLogSerializer


class SoftwareAssignmentViewSet(ModelViewSet):
    queryset = SoftwareAssignment.objects.all()
    serializer_class = SoftwareAssignmentSerializer
