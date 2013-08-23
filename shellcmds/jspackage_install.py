import sys
sys.path.insert(0,"lib")

from JumpScale import *

j.application.appname = "owpackage"
j.application.start()

import JumpScale.baselib.jspackages

print "upload package to blobstor"

package=j.packagesi.find()
package.install()


j.application.stop()