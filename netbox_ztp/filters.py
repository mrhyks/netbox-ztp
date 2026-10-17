from typing import ClassVar

from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_filters import BooleanFilter, CharFilter, FilterSet, ModelChoiceFilter

from dcim.models import Interface

from .models import OnboardedDevice, SoftwareAssignment, SourceDevice


class SourceDeviceFilterSet(FilterSet):
    q = CharFilter(method='search', label=_('Search'))
    enabled = BooleanFilter(field_name='enabled')
    interface = ModelChoiceFilter(field_name='interface', queryset=Interface.objects.all(), label=_('Interface'))

    class Meta:
        model = SourceDevice
        fields: ClassVar[list[str]] = ['q', 'enabled', 'interface']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(device__name__icontains=value)
            | Q(device__serial__icontains=value)
            | Q(device__id__icontains=value)
        )


class SourceDeviceFilterForm(forms.Form):
    q = forms.CharField(required=False, label=_('Search'))
    enabled = forms.NullBooleanField(required=False, label=_('Enabled'))
    interface = forms.ModelChoiceField(queryset=Interface.objects.none(), required=False, label=_('Interface'))


class OnboardedDeviceFilterSet(FilterSet):
    q = CharFilter(method='search', label=_('Search'))
    status = CharFilter(field_name='status', lookup_expr='icontains')

    class Meta:
        model = OnboardedDevice
        fields: ClassVar[list[str]] = ['q', 'status']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(serial_number__icontains=value)
            | Q(ip_address__icontains=value)
            | Q(mac_address__icontains=value)
            | Q(platform__icontains=value)
        )


class OnboardedDeviceFilterForm(forms.Form):
    q = forms.CharField(required=False, label=_('Search'))
    status = forms.CharField(required=False, label=_('Status'))

class SoftwareAssignmentFilterSet(FilterSet):
    q = CharFilter(method='search', label=_('Search'))
    device_types = CharFilter(field_name='device_types', lookup_expr='icontains')
    checksum = CharFilter(field_name='checksum', lookup_expr='icontains')
    version = CharFilter(field_name='version', lookup_expr='icontains')

    class Meta:
        model = SoftwareAssignment
        fields: ClassVar[list[str]] = ['q', 'device_types', 'checksum', 'version']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(device_types__icontains=value)
            | Q(checksum__icontains=value)
            | Q(version__icontains=value)
            | Q(description__icontains=value)
        )

class SoftwareAssignmentFilterForm(forms.Form):
    q = forms.CharField(required=False, label=_('Search'))
    device_types = forms.CharField(required=False, label=_('Device Types'))
    checksum = forms.CharField(required=False, label=_('Checksum'))
    version = forms.CharField(required=False, label=_('Version'))
    description = forms.CharField(required=False, label=_('Description'))