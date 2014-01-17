from JumpScale import j

import JumpScale.grid.geventws

j.application.start("reload")

client = j.servers.geventws.getClient("127.0.0.1", 4445, org="myorg", user=j.application.config.get('system.superadmin.login'), \
	passwd=j.application.config.get('gridmaster.superadminpasswd'),category="stats")

print client.listStatKeys(prefix="",memonly=False,avgmax=True)

from IPython import embed
print "DEBUG NOW ooo"
embed()

j.application.stop()