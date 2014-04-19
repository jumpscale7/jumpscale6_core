from JumpScale import j

descr = """
deploy grid node
"""

organization = "jumpscale"
author = "hendrik@vscalers.com"
license = "bsd"
version = "1.0"
category = "deploy.gridnode"
period = 1  # always in sec
startatboot = True
order = 1
enable = True
async = True
log = False


def action(node):

    c=node.cuapi

    print c.run("jpackage install -n grid -r --debug")
    print c.run("jpackage install -n grid_node -r --debug")
    print c.run("jpackage install --name processmanager -r --debug")
    print c.run("jpackage install -n workers -r --debug")
    print c.run("jsprocess start -c")
