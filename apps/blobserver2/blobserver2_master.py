
from JumpScale import j
import gevent

import JumpScale.grid.zdaemon

j.application.start("jumpscale:blobserver2master")
j.application.initGrid()

import JumpScale.baselib.blobstor2

j.logger.consoleloglevel = 2

j.servers.blobstor2.startMaster()

j.application.stop()


