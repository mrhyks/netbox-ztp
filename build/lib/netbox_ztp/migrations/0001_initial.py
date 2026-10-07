from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("dcim", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SourceDevice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("enabled", models.BooleanField(default=True)),
                ("scan_interval", models.IntegerField(default=300)),
                ("last_scan", models.DateTimeField(blank=True, null=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                (
                    "device",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ztp_source",
                        to="dcim.device",
                    ),
                ),
            ],
            options={
                "verbose_name": "Source device",
                "verbose_name_plural": "Source devices",
                "ordering": ("device__name",),
            },
        ),
        migrations.CreateModel(
            name="OnboardedDevice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("ip_address", models.GenericIPAddressField(protocol="IPv4")),
                ("mac_address", models.CharField(blank=True, max_length=17)),
                ("serial_number", models.CharField(max_length=128, unique=True)),
                ("platform", models.CharField(blank=True, max_length=128)),
                ("manufacturer", models.CharField(blank=True, max_length=128)),
                ("status", models.CharField(choices=[("new", "New"), ("onboarded", "Onboarded"), ("needs_update", "Needs Update"), ("failed", "Failed")], default="new", max_length=32)),
                ("rendered_config", models.TextField(blank=True)),
                ("last_seen", models.DateTimeField(auto_now=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "device",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="ztp_onboarded_device",
                        to="dcim.device",
                    ),
                ),
                (
                    "source_device",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="onboarded_devices",
                        to="netbox_ztp.sourcedevice",
                    ),
                ),
            ],
            options={
                "verbose_name": "Onboarded device",
                "verbose_name_plural": "Onboarded devices",
                "ordering": ("-created",),
            },
        ),
        migrations.CreateModel(
            name="ZTPLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("time", models.DateTimeField(auto_now_add=True)),
                ("level", models.CharField(choices=[("info", "Info"), ("success", "Success"), ("warning", "Warning"), ("error", "Error")], default="info", max_length=16)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True, protocol="IPv4")),
                ("serial_number", models.CharField(blank=True, max_length=128)),
                ("message", models.TextField()),
                (
                    "source_device",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="logs",
                        to="netbox_ztp.sourcedevice",
                    ),
                ),
            ],
            options={
                "verbose_name": "Log entry",
                "verbose_name_plural": "Log entries",
                "ordering": ("-time",),
            },
        ),
    ]
