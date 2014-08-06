# this must be in the beginning so things are patched before ever imported by other libraries
from gevent import monkey
# monkey.patch_all()
monkey.patch_socket()
monkey.patch_thread()
monkey.patch_time()

import time
from JumpScale import j
import JumpScale.portal

import sys

args=sys.argv
instance=args[1]

jp=j.packages.findNewest(name="portal",domain="jumpscale")
jp=jp.getInstance(instance)

j.application.start("portal")

j.logger.disable()

server=j.core.portal.getServer(hrd=jp.hrd_instance)
server.start()


j.application.stop()
