
from JumpScale import j

descr = """
fixed screwed-up default ubuntu dns setup
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
    cuapi.run("DEBIAN_FRONTEND=noninteractive apt-get remove unbound resolvconf -y")
    cuapi.run("echo nameserver 8.8.8.8 > /etc/resolv.conf")
