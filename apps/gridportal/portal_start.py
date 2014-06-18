#this must be in the beginning so things are patched before ever imported by other libraries
from gevent import monkey
# monkey.patch_all()
monkey.patch_socket()
monkey.patch_thread()
monkey.patch_time()
import time
from JumpScale import j
import JumpScale.portal

j.application.start("jumpscale:gridportal")
j.application.initGrid()

j.logger.disable()

j.core.portal.getServer().start()


j.application.stop()
