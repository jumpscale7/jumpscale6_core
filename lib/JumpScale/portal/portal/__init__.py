from JumpScale import j

from .PortalFactory import PortalFactory
j.base.loader.makeAvailable(j, 'core')
j.core.portal = PortalFactory()
