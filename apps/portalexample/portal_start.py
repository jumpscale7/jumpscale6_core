import time
from JumpScale import j
import JumpScale.portal

j.application.start("appserver6_test")

j.logger.disable()

j.manage.portal.startprocess()


j.application.stop()
