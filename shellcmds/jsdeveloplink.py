import sys
sys.path.insert(0,"lib")

from JumpScale import *

j.application.appname = "jslink"
j.application.start("jsinstallrepos",basedir="/opt/jumpscale/",appdir="/opt/jumpscale/apps/exampleapp/")

j.application.shellconfig.interactive=True

import JumpScale.baselib.platforms #gets access to ubuntu code
import JumpScale.baselib.owdeveltools


if j.system.platformtype.isLinux():
    j.system.platform.ubuntu.check()
    # j.develtools.installer.deployExamplesLibsGridPortal()
    # j.develtools.installer.deployDFS_IO()
    j.develtools.installer.link2code()

else:
    raise RuntimeError("JumpScale 6 is for now only supported on ubuntu or mint.")

