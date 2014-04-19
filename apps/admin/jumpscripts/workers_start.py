
from JumpScale import j

descr = """
workers restart
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "workers.restart"
period = 1  # always in sec
startatboot = True
order = 1
enable = True
async = False
log = False


def action(node):

    c=node.cuapi
    node.jpackageStart("workers","worker.py",nrtimes=5,retry=5)



