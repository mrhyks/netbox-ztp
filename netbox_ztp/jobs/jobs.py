
from netbox.plugins import get_plugin_config
from netbox_ztp.models import SourceDevice


class ArpCollectionJob:
    def __init__(self, object_id):
        self.object_id = object_id

    def run(self):
        # Implement the ARP collection logic here
        pass
    
    def get_arp_table(self):
        
        username = str(get_plugin_config('netbox_ztp', 'username'))
        password = str(get_plugin_config('netbox_ztp', 'password'))

        # Implement the logic to retrieve the ARP table using the username and password
        arp_table = []
        return arp_table
    
class OnboardDevices:
    def __init__(self, object: SourceDevice):
        self.object = object

    def run(self):
        username = str(get_plugin_config('netbox_ztp', 'username'))
        password = str(get_plugin_config('netbox_ztp', 'password'))
        print(f"[DEBUG] Running job on object_id={self.object.pk}, username={username}, password={password}")
        
