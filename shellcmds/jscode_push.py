import sys
sys.path.insert(0,"lib")

from JumpScale import *

j.application.appname = "jspush"
j.application.start()

import JumpScale.baselib.mercurial
j.application.shellconfig.interactive=True

for item in j.system.fs.listDirsInDir("/opt/code/jumpscale"):
    print "update/merge/commit/push for %s"%item
    cl=j.clients.mercurial.getClient(item)
    cl.updatemerge()
    cl.commit()
    cl.push()

