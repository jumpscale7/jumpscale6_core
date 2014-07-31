import time
from JumpScale import j

j.application.start("jumpscale:portalclienttest")
# j.application.initGrid()

import JumpScale.portal

#could be is no longer ok

client = j.core.a.portal.getPortalClient("127.0.0.1", port=$(portal.port), "$(portal.admin.passwd)")
system = client.getActor("system", "master", instance=0)

j.application.stop()
