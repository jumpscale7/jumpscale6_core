import sys
sys.path.insert(0,"lib")

from JumpScale import *

j.application.appname = "jsupdate"
j.application.start()


import JumpScale.baselib.mercurial
j.application.shellconfig.interactive=True

for item in j.system.fs.listDirsInDir("/opt/code/openwizzy"):
    print "update/merge/commit/push for %s"%item
    cl=j.clients.mercurial.getClient(item)
    cl.updatemerge()

