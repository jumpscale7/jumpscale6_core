from OpenWizzy import *

o.application.appname = "owcommit"
o.application.start()

import OpenWizzy.baselib.mercurial
import OpenWizzy.baselib.owdeveltools

o.application.shellconfig.interactive=True

o.develtools.installer.getCredentialsOpenWizzyRepo()


print o.develtools.installer.login

print o.develtools.installer.passwd

for item in o.system.fs.listDirsInDir("/opt/code/openwizzy"):
	url o.develtools.installer._getRemoteOWURL(item)
    print "update user for %s"%url
    from IPython import embed
    print "DEBUG NOW ooo"
    embed()
    
