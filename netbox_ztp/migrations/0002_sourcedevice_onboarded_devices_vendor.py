import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0251_fix_ltree_cascade_triggers'),
        ('netbox_ztp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sourcedevice',
            name='onboarded_devices_vendor',
            field=models.ForeignKey(
                help_text='Required vendor for onboarded devices.',
                on_delete=django.db.models.deletion.PROTECT,
                related_name='ztp_source_devices',
                to='dcim.manufacturer',
                null=True,
                blank=False,
            ),
        ),
    ]
