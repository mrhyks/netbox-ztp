from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_ztp', '0003_alter_sourcedevice_onboarded_devices_vendor'),
    ]

    operations = [
        migrations.AddField(
            model_name='softwareassignment',
            name='file_path',
            field=models.CharField(blank=True, help_text='Path to the software image file.', max_length=255),
        ),
    ]
