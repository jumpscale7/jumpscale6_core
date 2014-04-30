from JumpScale import j

descr = """
check timeout jobs
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "system.check.job.timeout"
period = 5 
enable=True
async=False

roles = []

def action():
    j.core.processmanager.cmds.worker.checkTimeouts()
    


