from OpenWizzy import o
from .PortalFactory import PortalClientFactory
from .PortalManage import PortalManage
o.base.loader.makeAvailable(o, 'core')
o.base.loader.makeAvailable(o, 'manage')
o.base.loader.makeAvailable(o, 'config')
o.core.portal = PortalClientFactory()
o.manage.portal = PortalManage()
