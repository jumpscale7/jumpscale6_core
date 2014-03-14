from JumpScale import j

descr = """
this is done by killing process manager which will be restarted by upstart in system
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "tools.processmanager.restart"
period = 0
enable=True
startatboot=False
async=False
roles = []

def action():
    j.application.stop()

    
