
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
    # c=node.cuapi
    node.executeCmds("jsprocess start", die=True,insandbox=True)

    
