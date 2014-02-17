from JumpScale import j

from JumpScale.core.config.IConfigBase import ConfigManagementItem, GroupConfigManagement, SingleConfigManagement
from JumpScale.core.config.JConfigBase import ConfiguredItem, ConfiguredItemGroup
from JumpScale.core.config.ConfigLib import ItemGroupClass, ItemSingleClass

class GitlabConfigManagementItem(ConfigManagementItem):
    CONFIGTYPE = "gitlab"
    DESCRIPTION = "gitlab account, key = accountname"
    KEYS = {"addr":"","login": "","passwd":"Password"}

    def ask(self):
        self.dialogAskString('login', 'Enter login')
        self.dialogAskPassword('passwd', 'Enter password for user "%s"' % self.params["login"])

GitlabConfigManagement = ItemGroupClass(GitlabConfigManagementItem)
