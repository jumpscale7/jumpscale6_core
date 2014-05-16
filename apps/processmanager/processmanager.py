#!/usr/bin/env python
#this must be in the beginning so things are patched before ever imported by other libraries
import gevent.monkey
# gevent.monkey.patch_all()

monkey.patch_socket()
monkey.patch_thread()
monkey.patch_time()
#gevent.monkey.patch_sys(stdin=True, stdout=True, stderr=True)


from JumpScale import j

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
