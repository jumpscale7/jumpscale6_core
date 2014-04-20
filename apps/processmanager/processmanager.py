#!/usr/bin/env python
from JumpScale import j

import JumpScale.grid.geventws
import time
import JumpScale.grid.processmanager

# import JumpScale.baselib.statmanager
# import JumpScale.baselib.graphite
# import psutil
# import importlib
# import sys

while j.system.net.tcpPortConnectionTest("127.0.0.1",7766)==False:
    time.sleep(0.1)
    print "cannot connect to redis main, will keep on trying forever, please start redis main (port 7766)"

while j.system.net.tcpPortConnectionTest("127.0.0.1",7768)==False:
    time.sleep(0.1)
    print "cannot connect to redis, will keep on trying forever, please start redis production (port 7768)"

import JumpScale.lib.diskmanager

import JumpScale.baselib.stataggregator

j.application.start("jumpscale:processmanager")

j.logger.consoleloglevel = 5
print 'start init grid'
j.core.grid.init()
print 'start processmanger'
j.core.processmanager.start()

j.application.stop()
