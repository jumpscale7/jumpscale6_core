
from JumpScale import j

descr = """
install shorewall with configs
"""

organization = "vscalers"
author = "tim@incubaid.com"
license = "bsd"
version = "1.0"
category = "deploy.platform.update"
period = 1  # always in sec
startatboot = True
order = 1
enable = True
async = True
log = False


def action(node):
    cuapi=node.cuapi
    cuapi.run("apt-get update")

    #IPv4 
    cuapi.run("apt-get install shorewall -y")
    node.uploadFromCfgDir("shorewall", "/etc/shorewall/")
    cuapi.run("sed -i 's/startup=0/startup=1/g' /etc/default/shorewall")
    cuapi.run("/etc/init.d/shorewall restart")

    #IPv6
    cuapi.run("apt-get install shorewall6 -y")
    node.uploadFromCfgDir("shorewall6", "/etc/shorewall6/")
    cuapi.run("sed -i 's/startup=0/startup=1/g' /etc/default/shorewall6")
    cuapi.run("/etc/init.d/shorewall6 restart")
