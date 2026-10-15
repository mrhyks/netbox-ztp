from typing import ClassVar

from netbox.plugins import PluginConfig


class NetBoxZTPConfig(PluginConfig):
    name = 'netbox_ztp'
    verbose_name = 'NetBox ZTP'
    description = 'Zero Touch Provisioning for NetBox'
    version = '0.1.0'
    base_url = 'ztp'
    required_settings: ClassVar[list[str]] = []
    default_settings: ClassVar[dict[str, object]] = {
        'arp_scan_interval': 300,
        'default_ssh_username': 'ztp',
        'default_ssh_password': 'ZTPzerodayPassword',
        'source_device_statuses': ['active', 'staged'],
    }


config = NetBoxZTPConfig
