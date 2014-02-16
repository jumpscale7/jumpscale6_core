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


def action(name, vxlanid, pubips):
    j.system.platform.lxc.networkSetPublic(name, pubips)
    # TODO: call networkSetPrivateVXLan with parameters
