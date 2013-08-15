from OpenWizzy import o
import OpenWizzy.grid.osismodel
from .PortalLoaderFactory import PortalLoaderFactory
o.base.loader.makeAvailable(o, 'core')
o.core.portalloader = PortalLoaderFactory()
