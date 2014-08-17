
from JumpScale import j

import JumpScale.grid.zdaemon

j.application.start("zdaemonclient")

j.logger.consoleloglevel = 2

client = j.core.zdaemon.getZDaemonClient(addr="127.0.0.1", port=5555, org="myorg", user="client1", passwd="1234", ssl=True,category="acategory")

print client.echo("Hello World.")

def perftest():
    nr = 3000
    j.base.timer.start()
    for i in range(nr):
        client.echo("Hello World.")

    j.base.timer.stop(nr)

#@todo JO can you do some profiling and see where we are slow?
perftest()

j.application.stop()
