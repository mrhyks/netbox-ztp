from typing import ClassVar

from django.utils.translation import gettext_lazy as _

from netbox.object_actions import ObjectAction


class IngestDevices(ObjectAction):
    """
    Ingest new devices into the system.
    """
    name = 'ingest_devices'
    label = _('Ingest Devices')
    multi = True
    permissions_required: ClassVar[set[str]] = {'ingest'}
