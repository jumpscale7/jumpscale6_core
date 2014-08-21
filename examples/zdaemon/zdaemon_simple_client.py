
from JumpScale import j

import JumpScale.grid.zdaemon

j.application.start("zdaemonclient")

j.logger.consoleloglevel = 6

client = j.core.zdaemon.getZDaemonClient(addr="127.0.0.1", port=3333, user="root", passwd="1234", ssl=False,category="acategory")

print client.echo("Hello World.")

# from IPython import embed
# print "DEBUG NOW main"
# embed()

j.application.stop()
