from JumpScale import j

from .WatchdogClient import *

j.base.loader.makeAvailable(j, 'tools')

j.tools.watchdogclient=WatchdogClient()
