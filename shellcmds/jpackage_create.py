import sys
sys.path.insert(0,"lib")

from JumpScale import j

j.application.appname = "jpackage"
j.application.start()

import JumpScale.baselib.jpackages

j.packagesi.createNewPackage()

j.application.stop()