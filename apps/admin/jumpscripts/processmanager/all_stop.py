
from JumpScale import j

descr = """
stop all jumpscale processes
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "all.stop"
period = 1  # always in sec
startatboot = True
order = 1
enable = True
async = False
log = True

def action(node):
    c=node.cuapi
    c.run("source /opt/jsbox/activate;jsprocess stop")

    
