import sys
sys.path.insert(0,"lib")

from OpenWizzy import *

o.application.appname = "owpackage"
o.application.start()

import OpenWizzy.baselib.jspackages

o.packagesi.publishAll()

o.application.stop()