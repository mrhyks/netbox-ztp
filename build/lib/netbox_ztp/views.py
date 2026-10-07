from django.conf import settings
from django.shortcuts import render

from .models import OnboardedDevice, SourceDevice, ZTPLog


def dashboard(request):
    return render(
        request,
        "netbox_ztp/dashboard.html",
        {
            "title": "Zero Touch Provisioning",
            "source_count": SourceDevice.objects.count(),
            "onboarded_count": OnboardedDevice.objects.count(),
            "log_count": ZTPLog.objects.count(),
        },
    )


def source_device_list(request):
    source_devices = SourceDevice.objects.select_related("device").all()
    return render(
        request,
        "netbox_ztp/source_device_list.html",
        {"title": "Source device", "source_devices": source_devices},
    )


def onboarded_device_list(request):
    onboarded_devices = OnboardedDevice.objects.select_related("source_device", "device").all()
    return render(
        request,
        "netbox_ztp/onboarded_device_list.html",
        {"title": "Onboarded devices", "onboarded_devices": onboarded_devices},
    )


def settings(request):
    plugin_cfg = getattr(settings, "PLUGINS_CONFIG", {}).get("netbox_ztp", {})
    context = {
        "title": "Settings",
        "arp_scan_interval": plugin_cfg.get("arp_scan_interval", 300),
        "default_ssh_username": plugin_cfg.get("default_ssh_username", "ztp"),
        "default_ssh_password": plugin_cfg.get("default_ssh_password", "ZTPzeradayPassword"),
    }
    return render(request, "netbox_ztp/settings.html", context)


def logs(request):
    logs = ZTPLog.objects.all()
    return render(request, "netbox_ztp/logs.html", {"title": "Logs", "logs": logs})
