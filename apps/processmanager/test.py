from JumpScale import j

import JumpScale.grid.geventws

j.application.start("reload")
j.application.initGrid()

client = j.servers.geventws.getClient("127.0.0.1", 4446, org="myorg", user="root", \
	passwd=j.application.config.get('grid.master.superadminpasswd'),category="stats")

print client.listStatKeys(prefix="",memonly=False,avgmax=True)

# from IPython import embed
# print "DEBUG NOW main process manager test"
# embed()

j.application.stop()
