from OpenWizzy import *

o.application.appname = "owlink"
o.application.start("owinstallrepos",basedir="/opt/openwizzy6/",appdir="/opt/openwizzy6/apps/exampleapp/")

o.application.shellconfig.interactive=True

import OpenWizzy.baselib.platforms #gets access to ubuntu code
import OpenWizzy.baselib.owdeveltools


if o.system.platformtype.isLinux():
    o.system.platform.ubuntu.check()
    # o.develtools.installer.deployExamplesLibsGridPortal()
    # o.develtools.installer.deployDFS_IO()
    o.develtools.installer.link2code()

else:
    raise RuntimeError("Openwizzy 6 is for now only supported on ubuntu or mint.")

