
from JumpScale import j

descr = """
update computenode from debug
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "deploy.processmanager.restart"
period = 1  # always in sec
startatboot = True
order = 1
enable = True
async = False
log = True

def action(node):
    c=node.cuapi

    node.serviceStart("processmanager","processmanager.py")    
    node.jpackageStart("workers","worker.py")
    c.run("jsprocess start")
    
    # if not c.file_exists("/usr/bin/jsredis"):
    #     c.run("ln -s /opt/code/jumpscale/unstable__jumpscale_core/shellcmds/jsredis /usr/bin/jsredis")
