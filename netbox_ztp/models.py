
from django.db import models
from django.urls import reverse

from dcim.models import Device, DeviceType, Interface, Manufacturer
from ipam.models import IPRange
from netbox.models import PrimaryModel

__all__ = [
    'OnboardedDevice',
    'SoftwareAssignment',
    'SourceDevice',
    'ZTPLog',
]


class SourceDevice(PrimaryModel):
    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name='ztp_source')
    interface = models.ForeignKey(
        Interface,
        on_delete=models.SET_NULL,
        related_name='ztp_source_devices',
        null=True,
        blank=True,
        help_text='Optional interface to restrict monitoring for this source device.',
    )
    ip_range = models.ForeignKey(
        IPRange,
        on_delete=models.SET_NULL,
        related_name='source_devices',
        null=True,
        blank=True,
        help_text='Optional IPv4/IPv6 range to accept',
    )
    onboarded_devices_vendor = models.ForeignKey(
        Manufacturer,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        related_name='ztp_source_devices',
        help_text='Required vendor for onboarded devices.',
    )
    enabled = models.BooleanField(default=True)
    scan_interval = models.IntegerField(default=300)
    last_scan = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(null=True, auto_now_add=True)
    updated = models.DateTimeField(null=True, auto_now=True)

    prerequisite_models = ('dcim.Device',)

    class Meta:
        ordering = ('device__name',)
        verbose_name = 'Source device'
        verbose_name_plural = 'Source devices'

    def __str__(self) -> str:
        return str(self.device)

    def get_absolute_url(self):
        return reverse('plugins:netbox_ztp:sourcedevice', args=[self.pk])


class OnboardedDevice(PrimaryModel):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('onboarded', 'Onboarded'),
        ('needs_update', 'Needs Update'),
        ('updating', 'Updating'),
        ('updated', 'Updated'),
        ('failed', 'Failed'),
    )

    device = models.OneToOneField(Device, on_delete=models.DO_NOTHING, related_name='ztp_onboarded_device')
    source_device = models.ForeignKey(SourceDevice, on_delete=models.PROTECT, related_name='onboarded_devices')
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='new')
    last_seen = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Onboarded device'
        verbose_name_plural = 'Onboarded devices'

    def __str__(self) -> str:
        return self.device.serial or self.device.primary_ip4.address if self.device.primary_ip4 else ''

    def delete(self, *args, **kwargs):
        device = self.device
        super().delete(*args, **kwargs)
        if device.pk:
            device.delete()

    def get_absolute_url(self):
        return reverse('plugins:netbox_ztp:onboardeddevice', args=[self.pk])


class ZTPLog(PrimaryModel):
    LEVEL_CHOICES = (
        ('info', 'Info'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    )

    time = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=16, choices=LEVEL_CHOICES, default='info')
    source_device = models.ForeignKey(SourceDevice, on_delete=models.SET_NULL, null=True, blank=True, related_name='logs')
    ip_address = models.GenericIPAddressField(protocol='IPv4', null=True, blank=True)
    serial_number = models.CharField(max_length=128, blank=True)
    message = models.TextField()

    class Meta:
        ordering = ('-time',)
        verbose_name = 'Log entry'
        verbose_name_plural = 'Log entries'

    def __str__(self) -> str:
        return f'{self.time.isoformat()} - {self.level}'

class SoftwareAssignment(PrimaryModel):
    device_types = models.ManyToManyField(DeviceType, related_name='software_assignments')
    checksum = models.CharField(max_length=128, blank=True)
    version = models.CharField(max_length=128)
    file_path = models.CharField(max_length=255, blank=True, help_text='Path to the software image file.')
    description = models.TextField(blank=True)

    prerequisite_models = ('dcim.DeviceType',)

    class Meta:
        ordering = ('device_types__model',)
        verbose_name = 'Software assignment'
        verbose_name_plural = 'Software assignments'

    def __str__(self) -> str:
        base = f'{", ".join([dt.model for dt in self.device_types.all()])} - {self.version}'
        return f'{base} - {self.file_path}' if self.file_path else base

    def get_absolute_url(self):
        if self.pk is None:
            return ''
        return reverse('plugins:netbox_ztp:softwareassignment', args=[self.pk])
    