from JumpScale import j
from .Screen import Screen
j.base.loader.makeAvailable(j, 'system.platform')
j.system.platform.screen = Screen()
