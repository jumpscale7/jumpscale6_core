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

j.application.start("jumpscale:jsprocessmanager")

j.logger.consoleloglevel = 5

j.core.grid.init()

j.core.processmanager.start()

j.application.stop()
