import sys
sys.path.insert(0,"lib")

from JumpScale import *

j.application.appname = "jspackage"
j.application.start()

import JumpScale.baselib.jspackages

j.packagesi.createNewPackage()

j.application.stop()