from OpenWizzy.core.config import ConfigManagementItem, ItemSingleClass, ItemGroupClass
from OpenWizzy import o

class BitbucketConfigManagementItem(ConfigManagementItem):
    CONFIGTYPE = "bitbucket"
    DESCRIPTION = "bitbucket account, key = accountname"
    KEYS = {"login": "","passwd":"Password"}

    def ask(self):
        self.dialogAskString('login', 'Enter login')
        self.dialogAskPassword('passwd', 'Enter password for user "%s"' % self.params["login"])

BitbucketConfigManagement = ItemGroupClass(BitbucketConfigManagementItem)
