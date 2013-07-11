from OpenWizzy.core.config import ConfigManagementItem, ItemGroupClass


class BlobStorConfigManagementItem(ConfigManagementItem):
    CONFIGTYPE = 'blobstor'
    DESCRIPTION = 'blobstor connection, key = name'
    KEYS = {
        'ftp': '',
        'http': '',
        'type': 'local',
        'localpath': '',
        'namespace': 'default'
    }

    def ask(self):
        self.dialogAskChoice('type', 'select type', ['local', 'ftphttp'], 'local')
        self.dialogAskString('namespace', 'Optional Namespace', 'default')
        self.dialogAskString('ftp', 'Optional FTP Location (full url location with login/passwd)')
        self.dialogAskString('http', 'Optional HTTP Location (for download only)')
        self.dialogAskString('localpath', 'Optional localpath', '/opt/qbase5/var/blobstor')

BlobStorConfigManagement = ItemGroupClass(BlobStorConfigManagementItem)
