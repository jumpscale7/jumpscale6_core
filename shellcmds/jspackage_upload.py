import sys
sys.path.insert(0,"lib")

from JumpScale import *

j.application.appname = "jspackage"
j.application.start()

import JumpScale.baselib.jspackages

print "upload package to blobstor"

package=j.packagesi.find()
if package<>None:
    package.upload()
else:
    raise RuntimeError("Could not find package.")


j.application.stop()