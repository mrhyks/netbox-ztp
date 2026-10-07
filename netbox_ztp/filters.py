from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_filters import BooleanFilter, CharFilter, FilterSet

from .models import OnboardedDevice, SourceDevice


class SourceDeviceFilterSet(FilterSet):
    q = CharFilter(method="search", label=_("Search"))
    enabled = BooleanFilter(field_name="enabled")

    class Meta:
        model = SourceDevice
        fields = ["q", "enabled"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(device__name__icontains=value)
            | Q(device__serial__icontains=value)
            | Q(device__id__icontains=value)
        )


class SourceDeviceFilterForm(forms.Form):
    q = forms.CharField(required=False, label=_("Search"))
    enabled = forms.NullBooleanField(required=False, label=_("Enabled"))


class OnboardedDeviceFilterSet(FilterSet):
    q = CharFilter(method="search", label=_("Search"))
    status = CharFilter(field_name="status", lookup_expr="icontains")

    class Meta:
        model = OnboardedDevice
        fields = ["q", "status"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(serial_number__icontains=value)
            | Q(ip_address__icontains=value)
            | Q(mac_address__icontains=value)
            | Q(platform__icontains=value)
        )
