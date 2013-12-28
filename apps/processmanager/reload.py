from JumpScale import j

import httplib
import thread
import time

import JumpScale.grid.geventws

j.application.start("reload")

client = j.servers.geventws.getClient("127.0.0.1", 4445, org="myorg", user=j.application.config.get('system.superadmin.login'), \
	passwd=j.application.config.get('system.superadmin.passwd'),category="processmanager")

# client.loadJumpscripts()
client.killGreenLets()

print "reloaded"

j.application.stop()