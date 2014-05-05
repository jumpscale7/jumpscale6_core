
from JumpScale import j

import time

j.application.start("jumpscale:watchdogmanager")

import JumpScale.baselib.watchdog.manager

while True:
    print "check"
    j.tools.watchdog.manager.checkWatchdogEvents()
    time.sleep(5)

j.application.stop()

