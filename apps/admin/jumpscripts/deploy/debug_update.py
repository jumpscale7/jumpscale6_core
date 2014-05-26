
from JumpScale import j

descr = """
update all code on platform
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "debug.update.code"
period = 1  # always in sec
startatboot = True
order = 1
enable = True
async = True
log = False


def action(node):
    CMDS="""
jpackage mdupdate
jscode update  -r '*' -a '*'
"""
    node.executeCmds(CMDS, die=True,insandbox=False)

