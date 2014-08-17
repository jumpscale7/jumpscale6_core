from JumpScale import j

j.application.start("lxcexamples_advanced")

import JumpScale.lib.lxc
import JumpScale.baselib.netconfig

reset=False

if reset:
    #DANGEROUS, will reset all your local netconfig of your system
    j.system.platform.lxc.resetNetworkConfigHostSystemDhcpSimple(pubinterface="eth0")

"""
lxc.hrd example config for network setup in Cairo office

lxc.bridge.public=br0
lxc.bridge.public.gw=192.168.20.1
lxc.bridge.management=br0
lxc.bridge.management.gw=192.168.40.1
lxc.nameserver=8.8.8.8
lxc.management.iprange=192.168.40.0/24
lxc.management.ipaddr=test:192.168.40.2,test3:192.168.40.3,test5:192.168.40.5,test4:192.168.40.4
lxc.defaults.pubinterface=eth0

firewall.hrd example from an lxc machine

firewall.nics.pub=pub0
firewall.nics.private=mgmt0
firewall.nics.dmz=dmz0
firewall.nics.vpn=
firewall.type=shorewall
firewall.ruletemplate=shorewall_dual_nic
"""

name = "test5"

j.system.platform.lxc.destroy(name)
ip = j.system.platform.lxc.create(name)

pubips=["192.168.21.194/23"]
j.system.platform.lxc.networkSetPublic(name, netname="pub0",bridge="br0",pubips=pubips)
j.system.platform.lxc.networkSetPrivateOnBridge(name, netname="dmz0",bridge="br0", ipaddresses=["192.168.30.37/24"])

j.system.platform.lxc.start(name)

#TODO we need to have a template with jumpscale core, shorewall and nginx jpackages installed
# for now, will create the fw object in another script


j.application.stop()