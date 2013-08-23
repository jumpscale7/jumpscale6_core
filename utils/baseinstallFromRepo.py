import sys
sys.path.insert(0,'../lib')

from JumpScale import j

import JumpScale.baselib.platforms #gets access to ubuntu code
import JumpScale.baselib.owdeveltools

do=j.system.installtools

j.application.start("owinstaller",basedir="/opt/openwizzy6/",appdir="/opt/openwizzy6/apps/exampleapp/")

if j.system.platformtype.isLinux():
    j.system.platform.ubuntu.check()
    j.develtools.installer.preparePlatformUbuntu()
    j.develtools.installer.link2code()


else:
    raise RuntimeError("JumpScale is for now only supported on ubuntu or mint.")

j.application.stop()
