from django.urls import include, path

from utilities.urls import get_model_urls

from . import views

app_name = "netbox_ztp"

urlpatterns = [
    path(
        "source-devices/",
        include(get_model_urls(app_name, "sourcedevice", detail=False)),
    ),
]
