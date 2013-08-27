import sys
sys.path.insert(0,"lib")

from JumpScale import j

j.application.appname = "jpackage"
j.application.start()

import JumpScale.baselib.jpackages

print "upload package to blobstor"

package=j.packagesi.find()
if package<>None:
    package.upload()
else:
    raise RuntimeError("Could not find package.")


j.application.stop()