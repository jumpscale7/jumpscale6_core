try:
    import ujson as json
except:
    import json

from JumpScale import j

import JumpScale.baselib.watchdogclient

j.application.start("jumpscale:watchdogclient")

j.tools.watchdogclient.send("cpu.core","OK",90)

j.application.stop()

