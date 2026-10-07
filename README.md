# NetBox Zero Touch Provisioning Plugin

This plugin monitors selected NetBox source devices, scans their ARP tables for unknown devices, connects to those hosts over SSH using default ZTP credentials, and captures their configuration state. Devices that are already known by serial number are reconciled against the current rendered configuration and updated when necessary.

## Included plugin pages

- Source device: Devices inside NetBox that are used as the scan source for ARP table discovery.
- Onboarded devices: Newly discovered devices that were reachable over SSH and accepted the default credentials.
- Settings: Plugin settings, including the ARP scan interval.
- Logs: Runtime logs generated during the provisioning workflow.

## Workflow

1. Scan ARP tables of configured source devices.
2. Identify devices that are not yet onboarded.
3. Attempt SSH access with the default credentials set in the plugin configuration.
4. If the SSH connection succeeds, onboard the device.
5. If the device serial number already exists and the rendered configuration differs from the current state, update it.
6. Log the operation result.
7. Repeat based on the configured ARP scan interval.

## Installation

Install the plugin into the NetBox environment and enable it by updating your NetBox configuration:

```python
PLUGINS = [
    "netbox_ztp",
]

PLUGINS_CONFIG = {
    "netbox_ztp": {
        "arp_scan_interval": 300,
        "default_ssh_username": "ztp",
        "default_ssh_password": "ZTPzerodayPassword",
    },
}
```

This should be placed in the NetBox config file at `/opt/netbox/netbox/netbox/configuration.py` in the `PLUGINS_CONFIG` section, or the equivalent plugin configuration area used by your installation.

## Default credentials

The default SSH credentials are configured by the plugin settings and intentionally match the requested bootstrap credential set:

- Username: `ztp`
- Password: `ZTPzeradayPassword`

These credentials are used when contacting new devices to validate reachability and retrieve the current device state.

## Example scheduler

The plugin includes a management command that can be triggered by cron or a systemd timer:

```bash
cd /opt/netbox/netbox
python3 manage.py ztp_scan
```

If you are using a recurring job scheduler, set the interval to the same value as `arp_scan_interval` to match the configured scan cadence.

## Implementation notes

- The plugin uses NetBox data models for source device tracking and onboarded device records.
- It uses NAPALM to scan ARP tables and verify device reachability over SSH.
- Onboarded devices are logged with the serial number, IP address, MAC address, and rendered configuration.
- The plugin stores audit logs in the database for troubleshooting and verification.
