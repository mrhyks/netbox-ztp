import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0251_fix_ltree_cascade_triggers'),
        ('netbox_ztp', '0004_softwareassignment'),
    ]

    operations = [
        migrations.AddField(
            model_name='sourcedevice',
            name='interface',
            field=models.ForeignKey(
                blank=True,
                help_text='Optional interface to restrict monitoring for this source device.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='ztp_source_devices',
                to='dcim.interface',
            ),
        ),
    ]
