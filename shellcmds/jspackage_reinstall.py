import sys
sys.path.insert(0,"lib")

from OpenWizzy import *

o.application.appname = "owpackage"
o.application.start()

import OpenWizzy.baselib.jspackages

print "upload package to blobstor"

package=o.packagesi.find()
package.install(reinstall=True)


o.application.stop()