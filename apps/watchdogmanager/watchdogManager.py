
from JumpScale import j

import time

j.application.start("jumpscale:watchdogmanager")

import JumpScale.baselib.watchdogmanager

while True:
    print "check"
    j.tools.watchdogmanager.checkWatchdogEvents()
    time.sleep(5)

j.application.stop()

