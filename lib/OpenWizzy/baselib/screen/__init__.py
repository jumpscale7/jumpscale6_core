from OpenWizzy import o
from .Screen import Screen
o.base.loader.makeAvailable(o, 'system.platform')
o.system.platform.screen = Screen()
