import sys
sys.path.insert(0,"lib")

from OpenWizzy import *

o.application.appname = "owcommit"
o.application.start()

import OpenWizzy.baselib.mercurial
import OpenWizzy.baselib.owdeveltools

o.application.shellconfig.interactive=True

o.develtools.installer.getCredentialsOpenWizzyRepo()

for item in o.system.fs.listDirsInDir("/opt/code/openwizzy"):
    itembase=o.system.fs.getBaseName(item)
    url=o.develtools.installer._getRemoteOWURL(itembase)
    path=o.system.fs.joinPaths(item,".hg","hgrc")
    print "change login info for %s to user %s"%(item,o.develtools.installer.login)
    C="""
[paths]
default = $url
"""    
    C=C.replace("$url",url)
    o.system.fs.writeFile(path,C)
    
