from OpenWizzy import *

o.application.appname = "owpackage"
o.application.start()

import OpenWizzy.baselib.jspackages

o.packagesi.publishAll()

o.application.stop()