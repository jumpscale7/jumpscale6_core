
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

#     node.serviceStop("redisp","redis/redisp")
#     node.serviceStop("redisc","redis/redisc")
#     node.serviceStart("redisp","redis/redisp")
#     node.serviceStart("redisc","redis/redisc")    

    c.run(". /opt/jsbox/activate ; jsprocess stop")

#     node.jpackageStop("workers","worker.py")
#     node.serviceReStart("processmanager","processmanager.py")    
#     node.jpackageStart("workers","worker.py")

    c.run(". /opt/jsbox/activate ; jsprocess start")

    
    # if not c.file_exists("/usr/bin/jsredis"):
    #     c.run("ln -s /opt/code/jumpscale/unstable__jumpscale_core/shellcmds/jsredis /usr/bin/jsredis")
