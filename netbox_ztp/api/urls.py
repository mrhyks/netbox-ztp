from rest_framework import routers

from .views import (
    OnboardedDeviceViewSet,
    SoftwareAssignmentViewSet,
    SourceDeviceViewSet,
    ZTPLogViewSet,
)

router = routers.DefaultRouter()
router.register('source-devices', SourceDeviceViewSet)
router.register('onboarded-devices', OnboardedDeviceViewSet)
router.register('software-assignments', SoftwareAssignmentViewSet)
router.register('ztp-logs', ZTPLogViewSet)

urlpatterns = router.urls
