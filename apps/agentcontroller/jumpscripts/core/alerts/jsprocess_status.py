
from JumpScale import j

descr = """
Check if all jsprocesses are running
"""

organization = "jumpscale"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
period = 60  # always in sec
timeout = period * 0.2 # max runtime = 20% of period
order = 1
enable = True
async = True
log = False
queue ='process'
roles = []


def action():
    for process in j.tools.startupmanager.getProcessDefs():
        if process.autostart and not process.isRunning():
            message = "Process %s:%s is not running" % (process.domain, process.name)
            j.errorconditionhandler.raiseOperationalWarning(message, 'monitoring')

