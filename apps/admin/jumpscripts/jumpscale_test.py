
from JumpScale import j

descr = """
install jumpscale sandbox
"""

organization = "jumpscale"
author = "hendrik@vscalers.com"
license = "bsd"
version = "1.0"
category = "deploy.js.sandbox"
period = 1  # always in sec
startatboot = True
order = 1
enable = True
async = True
log = False


def action(node):

    c=node.cuapi
    #with c.fabric.api.prefix('export JSBASE=/opt/jsbox'):
    c.run('env')
