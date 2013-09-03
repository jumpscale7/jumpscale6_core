from JumpScale import j
import JumpScale.grid.osismodel
from .PortalLoaderFactory import PortalLoaderFactory
j.base.loader.makeAvailable(j, 'core')
j.core.portalloader = PortalLoaderFactory()
