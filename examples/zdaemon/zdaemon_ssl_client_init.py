
from JumpScale import j

import JumpScale.grid.zdaemon

j.application.start("zdaemonclient")

j.logger.consoleloglevel = 2

client = j.core.zdaemon.getZDaemonClient(addr="127.0.0.1", port=5555, org="myorg", user="client1", passwd="1234", ssl=True, reset=True,category="acategory")
# will create private/pub keys for a client with name client1 in org: myorg

j.application.stop()
