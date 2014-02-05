from JumpScale import j

descr = """
configure DHCP
"""

name = "vfs_setapply_dhcpconfig"
category = "vfw"
organization = "jumpscale"
author = "khamisr@cloudscalers.com"
license = "bsd"
version = "1.0"
roles = ["*"]


def action(name, fromIP, toIP, interface):
    import JumpScale.lib.dhcp
    import JumpScale.lib.lxc

    host = j.system.platform.lxc.getip(name)
    password = j.application.config.get('vfw.password')

    cl = j.system.platform.dhcp.get(host, password)
    cl.configure(fromIP, toIP, interface)
    return "done"



