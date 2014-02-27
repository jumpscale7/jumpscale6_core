from JumpScale import j
import JumpScale.lib.lxc
import JumpScale.baselib.remote

descr = """
Sets network for LXC machine
"""

name = "vfs_setnetwork"
category = "vfw"
organization = "jumpscale"
author = "zains@incubaid.com"
license = "bsd"
version = "1.0"
roles = ["vfw.host"]


def action(name, vxlanid, pubips, dmzips):
    bridge = j.application.config.get('lxc.bridge.public')
    gateway = j.application.config.get('lxc.bridge.public.gw')
    j.system.platform.lxc.networkSetPublic(name, netname="pub0", bridge=bridge, pubips=pubips, gateway=gateway)
    j.system.platform.lxc.networkSetPrivateOnBridge(name, netname="dmz0", bridge=bridge, ipaddresses=dmzips)
    # TODO: call networkSetPrivateVXLan with parameters
