from datetime import timedelta
from ipaddress import ip_address

from django.conf import settings
from django.utils import timezone
from napalm import get_network_driver

from .models import OnboardedDevice, SourceDevice, ZTPLog


def _plugin_setting(name, default=None):
    plugin_settings = getattr(settings, "PLUGINS_CONFIG", {}).get("netbox_ztp", {})
    return plugin_settings.get(name, default)


def _log(level, message, source_device=None, ip_address=None, serial_number=""):
    return ZTPLog.objects.create(
        level=level,
        source_device=source_device,
        ip_address=ip_address,
        serial_number=serial_number,
        message=message,
    )


def _safe_ip(value):
    try:
        return str(ip_address(value))
    except ValueError:
        return None


def _rendered_config_matches(current_config, stored_config):
    if not stored_config:
        return False
    if not current_config:
        return False
    return current_config.strip() == stored_config.strip()


def _scan_arp_table(source_device):
    device = source_device.device
    if not getattr(device, "primary_ip", None):
        _log("warning", "Source device has no primary management IP", source_device=source_device)
        return []

    host = str(device.primary_ip.address.ip)
    username = _plugin_setting("default_ssh_username", "ztp")
    password = _plugin_setting("default_ssh_password", "ZTPzeradayPassword")

    try:
        driver = get_network_driver("ios")
        connection = driver(hostname=host, username=username, password=password, timeout=10)
        connection.open()
        arp_table = connection.get_arp_table() or []
        connection.close()
        return arp_table
    except Exception as exc:  # pragma: no cover - environment dependent
        _log("error", f"Unable to scan ARP table from source device {host}: {exc}", source_device=source_device, ip_address=host)
        return []


def _connect_to_device(ipv4_address, source_device):
    username = _plugin_setting("default_ssh_username", "ztp")
    password = _plugin_setting("default_ssh_password", "ZTPzeradayPassword")

    try:
        driver = get_network_driver("ios")
        connection = driver(hostname=ipv4_address, username=username, password=password, timeout=10)
        connection.open()
        facts = connection.get_facts() or {}
        config = connection.get_config(retrieve="running") if hasattr(connection, "get_config") else ""
        connection.close()
        return {
            "serial_number": facts.get("serial_number") or f"serial-{ipv4_address.replace('.', '')}",
            "platform": facts.get("os_version", "") or "",
            "manufacturer": facts.get("vendor", "ZTP"),
            "config": config,
        }
    except Exception as exc:  # pragma: no cover - environment dependent
        _log("warning", f"SSH connection failed for {ipv4_address}: {exc}", source_device=source_device, ip_address=ipv4_address)
        return None


def schedule_ztp_scan():
    interval = _plugin_setting("arp_scan_interval", 300)
    try:
        from django_rq import get_scheduler

        scheduler = get_scheduler("default")
        scheduler.schedule(
            scheduled_time=timezone.now() + timedelta(seconds=interval),
            func=run_ztp_scan,
            interval=interval,
            repeat=None,
            id="netbox_ztp_scan",
        )
        return True
    except Exception:  # pragma: no cover - optional dependency
        return False


def run_ztp_scan():
    for source_device in SourceDevice.objects.filter(enabled=True):
        candidates = []
        for entry in _scan_arp_table(source_device):
            if not isinstance(entry, dict):
                continue
            candidate_ip = _safe_ip(entry.get("ip"))
            if not candidate_ip:
                continue
            candidates.append((candidate_ip, entry.get("mac", "")))

        for candidate_ip, candidate_mac in candidates:
            existing = OnboardedDevice.objects.filter(ip_address=candidate_ip).first()
            if existing:
                _log("info", f"Device {candidate_ip} already onboarded", source_device=source_device, ip_address=candidate_ip, serial_number=existing.serial_number)
                continue

            connection_data = _connect_to_device(candidate_ip, source_device)
            if connection_data is None:
                continue

            serial_number = connection_data["serial_number"]
            onboarded = OnboardedDevice.objects.filter(serial_number=serial_number).first()
            if onboarded:
                if onboarded.rendered_config and not _rendered_config_matches(connection_data["config"], onboarded.rendered_config):
                    onboarded.rendered_config = connection_data["config"]
                    onboarded.status = "needs_update"
                    onboarded.save(update_fields=["rendered_config", "status", "last_seen"])
                    _log("success", f"Updated rendered config for {serial_number}", source_device=source_device, ip_address=candidate_ip, serial_number=serial_number)
                continue

            OnboardedDevice.objects.create(
                device=None,
                source_device=source_device,
                ip_address=candidate_ip,
                mac_address=candidate_mac,
                serial_number=serial_number,
                platform=connection_data["platform"],
                manufacturer=connection_data["manufacturer"],
                status="onboarded",
                rendered_config=connection_data["config"],
            )
            _log("success", f"Onboarded {serial_number} via ZTP", source_device=source_device, ip_address=candidate_ip, serial_number=serial_number)

        source_device.last_scan = timezone.now()
        source_device.save(update_fields=["last_scan"])

    return True
