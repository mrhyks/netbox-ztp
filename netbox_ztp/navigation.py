from netbox.plugins import PluginMenu, PluginMenuItem

menu = PluginMenu(
    label="ZTP",
    groups=(
        (
            "ZTP",
            (
                PluginMenuItem(
                    link="plugins:netbox_ztp:sourcedevice_list",
                    link_text="Source device",
                ),
                # PluginMenuItem(
                #     link="plugins:netbox_ztp:onboarded_device_list",
                #     link_text="Onboarded devices",
                # ),
                # PluginMenuItem(
                #     link="plugins:netbox_ztp:settings",
                #     link_text="Settings",
                # ),
                # PluginMenuItem(
                #     link="plugins:netbox_ztp:logs",
                #     link_text="Logs",
                # ),
            ),
        ),
    ),
)
