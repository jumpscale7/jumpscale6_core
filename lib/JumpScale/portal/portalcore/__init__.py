from JumpScale import j
from .PortalFactory import PortalClientFactory
from .PortalManage import PortalManage
j.base.loader.makeAvailable(j, 'core')
j.base.loader.makeAvailable(j, 'manage')
# j.base.loader.makeAvailable(j, 'config')
j.core.portal = PortalClientFactory()
j.manage.portal = PortalManage()
