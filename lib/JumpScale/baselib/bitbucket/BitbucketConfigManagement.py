from OpenWizzy import o

from OpenWizzy.core.config.IConfigBase import ConfigManagementItem, GroupConfigManagement, SingleConfigManagement
from OpenWizzy.core.config.QConfigBase import ConfiguredItem, ConfiguredItemGroup
from OpenWizzy.core.config.ConfigLib import ItemGroupClass, ItemSingleClass

class BitbucketConfigManagementItem(ConfigManagementItem):
    CONFIGTYPE = "bitbucket"
    DESCRIPTION = "bitbucket account, key = accountname"
    KEYS = {"login": "","passwd":"Password"}

    def ask(self):
        self.dialogAskString('login', 'Enter login')
        self.dialogAskPassword('passwd', 'Enter password for user "%s"' % self.params["login"])

BitbucketConfigManagement = ItemGroupClass(BitbucketConfigManagementItem)
