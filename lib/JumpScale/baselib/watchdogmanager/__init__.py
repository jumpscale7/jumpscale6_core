from JumpScale import j

from .WatchdogFactory import *

j.base.loader.makeAvailable(j, 'tools')

j.tools.watchdogmanager=WatchdogFactory()
