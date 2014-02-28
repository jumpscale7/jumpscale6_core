from JumpScale import j

descr = """
check if workers are running
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "system.checkworkers"
period = 2
enable=True
startatboot=False
async=False
roles = ["*"]


def action():
    import psutil
    nrworkers=0
    for proc in psutil.process_iter():
        name2=" ".join(proc.cmdline)
        if name2.find("python worker.py")<>-1:
            nrworkers+=1

    if nrworkers<4:
        j.tools.startupmanager.startJPackage(j.packages.findNewest(name="workers"))
    
