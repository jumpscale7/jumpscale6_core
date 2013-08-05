from OpenWizzy import o
from .SSL import SSL
o.base.loader.makeAvailable(o, 'tools')
o.tools.ssl = SSL()
