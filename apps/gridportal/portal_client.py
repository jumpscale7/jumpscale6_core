import time
from JumpScale import j

j.application.start("appserver6_client")

import JumpScale.portal

client = j.core.a.portal.getPortalClient("127.0.0.1", port=9900, "1234")
system = client.getActor("system", "master", instance=0)

j.application.stop()
