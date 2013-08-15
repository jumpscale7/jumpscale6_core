from OpenWizzy import o
from .GridFactory import GridFactory
o.base.loader.makeAvailable(o, 'core')
o.core.grid = GridFactory()
