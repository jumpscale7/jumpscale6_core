import sys
sys.path.insert(0,"lib")

from JumpScale import *

j.application.appname = "reinstall"
j.application.start()

import JumpScale.baselib.platforms #gets access to ubuntu code
import JumpScale.baselib.owdeveltools

j.application.shellconfig.interactive=True


do=j.system.installtools

j.application.start("jsinstallrepos",basedir="/opt/jumpscale/",appdir="/opt/jumpscale/apps/exampleapp/")

print "REINSTALL JUMPSCALE ONTO OS."

if j.system.platformtype.isLinux():
    j.system.platform.ubuntu.check()
    j.develtools.installer.deployExamplesLibsGridPortal()
    j.develtools.installer.deployDFS_IO()

    for item in j.system.fs.listDirsInDir("/opt/code/jumpscale"):
        print "update/merge/commit/push for %s"%item
        cl=j.clients.mercurial.getClient(item)
        cl.updatemerge()

    j.develtools.installer.link2code()

else:
    raise RuntimeError("Jumpscale is for now only supported on ubuntu or mint.")

