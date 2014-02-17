from JumpScale import j

descr = """
This jumpscript returns network info
"""

name = "getnetworkinfo"
category = "monitoring"
organization = "opencode"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
roles = ["grid.node"]


def action():
    return j.system.net.getNetworkInfo()



