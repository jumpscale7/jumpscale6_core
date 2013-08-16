import sys
sys.path.insert(0,"lib")

from OpenWizzy import *

o.application.appname = "owcommit"
o.application.start()

import OpenWizzy.baselib.mercurial


o.application.shellconfig.interactive=True

for item in o.system.fs.listDirsInDir("/opt/code/openwizzy"):
    print "update/merge/commit/push for %s"%item
    cl=o.clients.mercurial.getClient(item)
    cl.commit()

