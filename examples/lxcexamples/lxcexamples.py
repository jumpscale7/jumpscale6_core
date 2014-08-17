from JumpScale import j
from JumpScale import j

j.application.start("lxcexamples")

import JumpScale.lib.lxc
import JumpScale.baselib.netconfig

reset=True

if reset:
    #DANGEROUS, will reset all your local netconfig of your system
    j.system.platform.lxc.resetNetworkConfigHostSystemDhcpSimple()

s

name="test3"
j.system.platform.lxc.destroy(name)
ip=j.system.platform.lxc.create(name)

pubips=["192.168.1.207/24"]#,"192.168.1.21/24"]
j.system.platform.lxc.networkSetPublic(name, netname="pub0",bridge="br0",pubips=pubips)
j.system.platform.lxc.networkSetPrivateOnBridge(name, netname="dmz0",bridge="br0", ipaddresses=["192.168.30.22/24"])

j.system.platform.lxc.start(name)

print j.system.platform.lxc.list()


j.application.stop()