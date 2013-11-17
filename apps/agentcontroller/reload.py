from JumpScale import j

import httplib
import thread
import time

import JumpScale.grid.geventws

j.application.start("reload")

client = j.servers.geventws.getClient("127.0.0.1", 4444, org="myorg", user="admin", passwd="1234", \
    roles=["system.1", "hypervisor.1"],category="agent")

client.loadJumpscripts()

print "reloaded"

j.application.stop()