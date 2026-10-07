from django.db import models

from dcim.models import Device


class SourceDevice(models.Model):
    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name="ztp_source")
    enabled = models.BooleanField(default=True)
    scan_interval = models.IntegerField(default=300)
    last_scan = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("device__name",)
        verbose_name = "Source device"
        verbose_name_plural = "Source devices"

    def __str__(self) -> str:
        return str(self.device)


class OnboardedDevice(models.Model):
    STATUS_CHOICES = (
        ("new", "New"),
        ("onboarded", "Onboarded"),
        ("needs_update", "Needs Update"),
        ("failed", "Failed"),
    )

    device = models.OneToOneField(Device, on_delete=models.SET_NULL, related_name="ztp_onboarded_device", null=True, blank=True)
    source_device = models.ForeignKey(SourceDevice, on_delete=models.PROTECT, related_name="onboarded_devices")
    ip_address = models.GenericIPAddressField(protocol="IPv4")
    mac_address = models.CharField(max_length=17, blank=True)
    serial_number = models.CharField(max_length=128, unique=True)
    platform = models.CharField(max_length=128, blank=True)
    manufacturer = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="new")
    rendered_config = models.TextField(blank=True)
    last_seen = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created",)
        verbose_name = "Onboarded device"
        verbose_name_plural = "Onboarded devices"

    def __str__(self) -> str:
        return self.serial_number or self.ip_address


class ZTPLog(models.Model):
    LEVEL_CHOICES = (
        ("info", "Info"),
        ("success", "Success"),
        ("warning", "Warning"),
        ("error", "Error"),
    )

    time = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=16, choices=LEVEL_CHOICES, default="info")
    source_device = models.ForeignKey(SourceDevice, on_delete=models.SET_NULL, null=True, blank=True, related_name="logs")
    ip_address = models.GenericIPAddressField(protocol="IPv4", null=True, blank=True)
    serial_number = models.CharField(max_length=128, blank=True)
    message = models.TextField()

    class Meta:
        ordering = ("-time",)
        verbose_name = "Log entry"
        verbose_name_plural = "Log entries"

    def __str__(self) -> str:
        return f"{self.time.isoformat()} - {self.level}"
