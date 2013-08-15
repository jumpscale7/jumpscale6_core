from OpenWizzy import *

o.application.appname = "owpackage"
o.application.start()

import OpenWizzy.baselib.jspackages

print "upload package to blobstor"

package=o.packagesi.find()
package.upload()

from IPython import embed
print "DEBUG NOW upload"
embed()


o.application.stop()