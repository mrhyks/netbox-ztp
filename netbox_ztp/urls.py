from django.urls import include, path

from utilities.urls import get_model_urls

from . import views  # noqa: F401

app_name = 'netbox_ztp'

urlpatterns = [
    path('source-devices/', include(get_model_urls(app_name, 'sourcedevice', detail=False))),
    path('source-devices/<int:pk>/', include(get_model_urls(app_name, 'sourcedevice'))),
    path('onboarded-devices/', include(get_model_urls(app_name, 'onboardeddevice', detail=False))),
    path('onboarded-devices/<int:pk>/', include(get_model_urls(app_name, 'onboardeddevice'))),
    path('software-assignments/', include(get_model_urls(app_name, 'softwareassignment', detail=False))),
    path('software-assignments/<int:pk>/', include(get_model_urls(app_name, 'softwareassignment'))),
    path('ztp-logs/', include(get_model_urls(app_name, 'ztplog', detail=False))),
]
