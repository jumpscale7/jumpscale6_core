import os
import struct

from JumpScale import j

j.application.start("rsync")

import JumpScale.baselib.rsync


j.system.fs.createDir("/tmp/server")

server=j.tools.rsync.getServer("/tmp/server")

server.addUser("auser","test")
server.addUser("auser2","test2")
server.addSecret("actions")
server.addSecret("jpackages_jumpscale")

server.start(background=True)

j.application.stop()
