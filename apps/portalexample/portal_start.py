import time
from JumpScale import j
import JumpScale.portal

j.application.start("jumpscale:gridportal")
j.application.initGrid()

j.logger.disable()

j.core.portal.getServer().start()


j.application.stop()
