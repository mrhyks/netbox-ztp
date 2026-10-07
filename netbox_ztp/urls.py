from django.urls import path

from .views import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("source-devices/", views.source_device_list, name="source_device_list"),
    path("onboarded-devices/", views.onboarded_device_list, name="onboarded_device_list"),
    path("settings/", views.settings, name="settings"),
    path("logs/", views.logs, name="logs"),
]
