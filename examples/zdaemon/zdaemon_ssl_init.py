
from JumpScale import j

import JumpScale.grid.zdaemon

j.application.start("zdaemon")

j.logger.consoleloglevel = 2

j.core.zdaemon.initSSL4Server("myorg", "servertest")

j.application.stop()
