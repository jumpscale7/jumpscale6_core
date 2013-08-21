from OpenWizzy import o
from .ImageLib import ImageLib
o.base.loader.makeAvailable(o, 'tools')
o.tools.imagelib = ImageLib()
