from JumpScale import j

descr = """
see if all processes are still running, if not restart them.
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "startupmanager.check"
period = 60 #always in sec
enable=False

def action():
    j.tools.startupmanager.startProcess(None,None)

