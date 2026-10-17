import ipaddress

from django.db import models
from django.urls import reverse

from dcim.models import Device, DeviceType, Interface
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
        ('failed', 'Failed'),
    )

    device = models.OneToOneField(Device, on_delete=models.SET_NULL, related_name='ztp_onboarded_device', null=True, blank=True)
    source_device = models.ForeignKey(SourceDevice, on_delete=models.PROTECT, related_name='onboarded_devices')
    ip_address = models.GenericIPAddressField(protocol='IPv4')
    mac_address = models.CharField(max_length=17, blank=True)
    serial_number = models.CharField(max_length=128, unique=True)
    platform = models.CharField(max_length=128, blank=True)
    manufacturer = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='new')
    rendered_config = models.TextField(blank=True)
    last_seen = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Onboarded device'
        verbose_name_plural = 'Onboarded devices'

    def __str__(self) -> str:
        return self.serial_number or self.ip_address

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
    description = models.TextField(blank=True)
    
    prerequisite_models = ('dcim.DeviceType',)

    class Meta:
        ordering = ('device_types__model',)
        verbose_name = 'Software assignment'
        verbose_name_plural = 'Software assignments'

    def __str__(self) -> str:
        return f'{", ".join([dt.model for dt in self.device_types.all()])} - {self.version}'
    def get_absolute_url(self):
        if self.pk is None:
            return ''
        return reverse('plugins:netbox_ztp:softwareassignment', args=[self.pk])
    