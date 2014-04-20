
from JumpScale import j

descr = """
echo
"""


organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "deploy.echo"
period = 1  # always in sec
startatboot = True
order = 1
enable = True
async = True
log = False


def action(node):

    cuapi=node.cuapi
    out=""
    out+=cuapi.run("ls /")
    out+=cuapi.run("ping www.google.com -c 1 -W 1 -w 2")
    return out
