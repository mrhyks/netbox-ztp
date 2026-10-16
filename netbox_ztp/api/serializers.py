from netbox.api.serializers import PrimaryModelSerializer
from netbox_ztp.models import OnboardedDevice, SoftwareAssignment, SourceDevice, ZTPLog

__all__ = (
    'OnboardedDeviceSerializer',
    'SoftwareAssignmentSerializer',
    'SourceDeviceSerializer',
    'ZTPLogSerializer',
)


class SourceDeviceSerializer(PrimaryModelSerializer):
    class Meta:
        model = SourceDevice
        fields = '__all__'


class OnboardedDeviceSerializer(PrimaryModelSerializer):
    class Meta:
        model = OnboardedDevice
        fields = '__all__'


class ZTPLogSerializer(PrimaryModelSerializer):
    class Meta:
        model = ZTPLog
        fields = '__all__'


class SoftwareAssignmentSerializer(PrimaryModelSerializer):
    class Meta:
        model = SoftwareAssignment
        fields = '__all__'
