
from JumpScale import j

descr = """
clean redis
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "deploy.redis.clean"
period = 1  # always in sec
startatboot = True
order = 1
enable = True
async = False
log = False


def action(node):

    c=node.cuapi

    node.serviceStop("redisp","redis/redisp")
    node.serviceStop("redisc","redis/redisc")
    node.serviceStop("processmanager","processmanager.py")
    node.jpackageStop("workers","worker.py")

    node.executeCmds("rm -rf /opt/redis/",die=False)

    c.run("jpackage install -n redis -r")

    node.serviceStart("redisp","redis/redisp")
    node.serviceStart("redisc","redis/redisc")
    node.serviceStart("processmanager","processmanager.py")

    node.jpackageStart("workers","worker.py",nrtimes=5,retry=5)



