import time
from JumpScale import j

j.application.start("jumpscale:portalclientest")
j.application.initGrid()

import JumpScale.portal

client = j.core.a.portal.getPortalClient("127.0.0.1", port=81, "1234")
system = client.getActor("system", "master", instance=0)


j.application.stop()
