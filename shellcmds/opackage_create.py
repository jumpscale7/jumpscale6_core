from OpenWizzy import *

o.application.appname = "jspackage"
o.application.start()

import OpenWizzy.baselib.jspackages

o.packagesi.createNewPackage()

o.application.stop()