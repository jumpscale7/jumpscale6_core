import sys
sys.path.append('../lib')

from JumpScale import *

import JumpScale.baselib.platforms #gets access to ubuntu code
import JumpScale.baselib.owdeveltools

do=j.system.installtools

j.application.start("jsinstallrepos",basedir="/opt/jumpscale6/",appdir="/opt/jumpscale6/apps/exampleapp/")

if j.system.platformtype.isLinux():
    j.system.platform.ubuntu.check()
    j.develtools.installer.deployExamplesLibsGridPortal()
    j.develtools.installer.deployDFS_IO()

else:
    raise RuntimeError("JumpScale is for now only supported on ubuntu or mint.")
