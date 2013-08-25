from JumpScale import j
from .ImageLib import ImageLib
j.base.loader.makeAvailable(j, 'tools')
j.tools.imagelib = ImageLib()
