from JumpScale import j
import JumpScale.grid.osismodel
from .PortalLoaderFactory import PortalLoaderFactory
from .ActorsInfo import ActorsInfo

j.base.loader.makeAvailable(j, 'core')
j.core.portalloader = PortalLoaderFactory()
j.core.portalloader.actorsinfo=ActorsInfo()