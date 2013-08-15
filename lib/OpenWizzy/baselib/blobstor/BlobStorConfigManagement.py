
from OpenWizzy.core.config.IConfigBase import ConfigManagementItem, GroupConfigManagement, SingleConfigManagement
from OpenWizzy.core.config.QConfigBase import ConfiguredItem, ConfiguredItemGroup
from OpenWizzy.core.config.ConfigLib import ItemGroupClass, ItemSingleClass

class BlobStorConfigManagementItem(ConfigManagementItem):
    CONFIGTYPE = 'blobstor'
    DESCRIPTION = 'blobstor connection, key = name'
    KEYS = {
        'ftp': '',
        'http': '',
        'type': 'local',
        'localpath': '',
        'namespace': 'o.'
    }

    def ask(self):
        self.dialogAskChoice('type', 'select type', ['local', 'ftphttp'], 'local')
        self.dialogAskString('namespace', 'Optional Namespace', 'o.')
        self.dialogAskString('ftp', 'Optional FTP Location (full url location with login/passwd)')
        self.dialogAskString('http', 'Optional HTTP Location (for download only)')
        self.dialogAskString('localpath', 'Optional localpath', '/opt/openwizzy6/var/blobstor')

BlobStorConfigManagement = ItemGroupClass(BlobStorConfigManagementItem)
