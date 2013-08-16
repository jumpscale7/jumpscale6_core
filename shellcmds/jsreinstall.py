import sys
sys.path.insert(0,"lib")

from OpenWizzy import *

o.application.appname = "reinstall"
o.application.start()

import OpenWizzy.baselib.platforms #gets access to ubuntu code
import OpenWizzy.baselib.owdeveltools

o.application.shellconfig.interactive=True


do=o.system.installtools

o.application.start("owinstallrepos",basedir="/opt/openwizzy6/",appdir="/opt/openwizzy6/apps/exampleapp/")

print "REINSTALL OPENWIZZY ONTO OS."

if o.system.platformtype.isLinux():
    o.system.platform.ubuntu.check()
    o.develtools.installer.deployExamplesLibsGridPortal()
    o.develtools.installer.deployDFS_IO()

    for item in o.system.fs.listDirsInDir("/opt/code/openwizzy"):
        print "update/merge/commit/push for %s"%item
        cl=o.clients.mercurial.getClient(item)
        cl.updatemerge()

    o.develtools.installer.link2code()

else:
    raise RuntimeError("Openwizzy 6 is for now only supported on ubuntu or mint.")

