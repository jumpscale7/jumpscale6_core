from JumpScale import j
import JumpScale.lib.dhcp
import JumpScale.lib.lxc

descr = """
configure DHCP
"""

name = "vfs_setapply_dhcpconfig"
category = "vfw"
organization = "jumpscale"
author = "khamisr@cloudscalers.com"
license = "bsd"
version = "1.0"
roles = []


def action(name, fromIP, toIP, interface):
    host = j.system.platform.lxc.getIp(name)
    password = j.application.config.get('system.superadmin.passwd')

    cl = j.system.platform.dhcp.get(host, password)
    cl.configure(fromIP, toIP, interface)



