from django.db import migrations


def reconcile_ztplog_device_fk(apps, schema_editor):
    """Repair ZTPLog schema when migration history says up-to-date but DB is still legacy."""
    connection = schema_editor.connection

    if connection.vendor != "postgresql":
        return

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'netbox_ztp_ztplog'
            """
        )
        columns = {row[0] for row in cursor.fetchall()}

        if "device_id" not in columns:
            cursor.execute("ALTER TABLE netbox_ztp_ztplog ADD COLUMN device_id bigint NULL")
            columns.add("device_id")

        if "serial_number" in columns:
            cursor.execute(
                """
                UPDATE netbox_ztp_ztplog AS log
                SET device_id = d.id
                FROM dcim_device AS d
                WHERE log.device_id IS NULL
                  AND log.serial_number IS NOT NULL
                  AND log.serial_number <> ''
                  AND d.serial = log.serial_number
                """
            )

        if "ip_address" in columns:
            cursor.execute(
                """
                UPDATE netbox_ztp_ztplog AS log
                SET device_id = d.id
                FROM dcim_device AS d
                JOIN ipam_ipaddress AS ip ON ip.id = d.primary_ip4_id
                WHERE log.device_id IS NULL
                  AND log.ip_address IS NOT NULL
                  AND host(ip.address) = host(log.ip_address)
                """
            )

        cursor.execute(
            "CREATE INDEX IF NOT EXISTS netbox_ztp_ztplog_device_id_idx ON netbox_ztp_ztplog (device_id)"
        )

        cursor.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'netbox_ztp_ztplog_device_id_fk'
                ) THEN
                    ALTER TABLE netbox_ztp_ztplog
                    ADD CONSTRAINT netbox_ztp_ztplog_device_id_fk
                    FOREIGN KEY (device_id)
                    REFERENCES dcim_device (id)
                    DEFERRABLE INITIALLY DEFERRED;
                END IF;
            END $$;
            """
        )

        cursor.execute("ALTER TABLE netbox_ztp_ztplog DROP COLUMN IF EXISTS ip_address")
        cursor.execute("ALTER TABLE netbox_ztp_ztplog DROP COLUMN IF EXISTS serial_number")


def reverse_noop(apps, schema_editor):
    # Intentionally left empty: this repair migration is one-way.
    return


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_ztp", "0007_remove_sourcedevice_ip_range_and_more"),
    ]

    operations = [
        migrations.RunPython(reconcile_ztplog_device_fk, reverse_code=reverse_noop),
    ]
