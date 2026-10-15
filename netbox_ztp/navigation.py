from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

COL_ADD = 'mdi mdi-plus'
COL_IMPORT = 'mdi mdi-upload'

menu = PluginMenu(
    label='ZTP',
    groups=(
        (
            'ZTP',
            (
                PluginMenuItem(
                    link='plugins:netbox_ztp:sourcedevice_list',
                    link_text='Source device',
                    buttons=(
                        PluginMenuButton(
                            link='plugins:netbox_ztp:sourcedevice_add',
                            title='Add',
                            icon_class=COL_ADD,
                            permissions=('netbox_ztp.add_sourcedevice',)
                        ),
                        PluginMenuButton(
                            link='plugins:netbox_ztp:sourcedevice_bulk_import',
                            title='Import',
                            icon_class=COL_IMPORT,
                            permissions=('netbox_ztp.add_sourcedevice',)
                        ),
                    )
                ),
                PluginMenuItem(
                    link='plugins:netbox_ztp:onboarded_device_list',
                    link_text='Onboarded devices',
                ),
                # PluginMenuItem(
                #     link='plugins:netbox_ztp:settings',
                #     link_text='Settings',
                # ),
                # PluginMenuItem(
                #     link='plugins:netbox_ztp:logs',
                #     link_text='Logs',
                # ),
            ),
        ),
    ),
)
