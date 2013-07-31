import sys
sys.path.append('../lib')

from OpenWizzy import *

import OpenWizzy.baselib.platforms #gets access to ubuntu code
import OpenWizzy.baselib.owdeveltools

do=o.system.installtools

o.application.start("owinstallrepos",basedir="/opt/openwizzy6/",appdir="/opt/openwizzy6/apps/exampleapp/")

if o.system.platformtype.isLinux():
    o.system.platform.ubuntu.check()
    o.develtools.installer.deployExamplesLibsGridPortal()
    o.develtools.installer.deployDFS_IO()

else:
    raise RuntimeError("Openwizzy 6 is for now only supported on ubuntu or mint.")
