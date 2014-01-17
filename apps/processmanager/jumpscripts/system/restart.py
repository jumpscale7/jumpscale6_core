from JumpScale import j

descr = """
send all gathered statistics to carbon (backend of monitoring)
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "tools.restart"
period = 12*3600 #every 12h restart full process
enable=True
startatboot=False

import sys,fcntl,os

def action():
    jumpscript=j.processmanager.jumpscripts.jumpscripts["jumpscale_restart"]
    jumpscript.enable=False #this to make sure it wont run, will be reloaded after restart anyhow
    j.processmanager.jumpscripts.run()
    args = sys.argv[:]
    args.insert(0, sys.executable)
    max_fd = 1024
    for fd in range(3, max_fd):
        try:
            flags = fcntl.fcntl(fd, fcntl.F_GETFD)
        except IOError:
            continue
        fcntl.fcntl(fd, fcntl.F_SETFD, flags | fcntl.FD_CLOEXEC)
    os.chdir("/opt/jumpscale/apps/processmanager/")
    os.execv(sys.executable, args)    

