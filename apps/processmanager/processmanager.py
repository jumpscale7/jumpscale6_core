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


import JumpScale.lib.diskmanager

import JumpScale.baselib.stataggregator

j.application.start("jumpscale:processmanager")

j.logger.consoleloglevel = 5
print 'start init grid'
j.core.grid.init()
print 'start processmanger'
j.core.processmanager.start()

j.application.stop()
