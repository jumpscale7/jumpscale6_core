import sys
sys.path.insert(0,'../lib')

from OpenWizzy import o

import OpenWizzy.baselib.platforms #gets access to ubuntu code
import OpenWizzy.baselib.owdeveltools

do=o.system.installtools

o.application.start("owinstaller",basedir="/opt/openwizzy6/",appdir="/opt/openwizzy6/apps/exampleapp/")

if o.system.platformtype.isLinux():
    o.system.platform.ubuntu.check()
    o.develtools.installer.preparePlatformUbuntu()
    o.develtools.installer.link2code()


else:
    raise RuntimeError("Openwizzy 6 is for now only supported on ubuntu or mint.")

o.application.stop()
