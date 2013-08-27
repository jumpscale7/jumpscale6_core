import sys
sys.path.insert(0,"lib")

from JumpScale import j

j.application.appname = "jscommit"
j.application.start()

import JumpScale.baselib.mercurial
import JumpScale.baselib.jsdeveltools

j.application.shellconfig.interactive=True

j.develtools.installer.getCredentialsJumpScaleRepo()

for item in j.system.fs.listDirsInDir("/opt/code/jumpscale"):
    itembase=j.system.fs.getBaseName(item)
    url=j.develtools.installer._getRemoteOWURL(itembase)
    path=j.system.fs.joinPaths(item,".hg","hgrc")
    print "change login info for %s to user %s"%(item,j.develtools.installer.login)
    C="""
[paths]
default = $url
"""    
    C=C.replace("$url",url)
    j.system.fs.writeFile(path,C)
    
