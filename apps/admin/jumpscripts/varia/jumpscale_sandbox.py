
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
    c.run('curl http://install.jumpscale.org:85/jsbox_unstable.sh | sh')
    c.run('export JSBASE=/opt/jsbox')
    c.run('echo export JSBASE=/opt/jsbox >> /root/.profile')
