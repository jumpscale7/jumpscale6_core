from pylabs.InitBase import *


q.application.appname = "deply"
q.application.start()

cl = q.remote.cluster.create("test", "test", ["192.168.80.13"], "rooter")

# cl.sshtest()

cl.ubuntuPackageUpdateUpgrade()

from pylabs.Shell import ipshellDebug, ipshell
print "DEBUG NOW main"
ipshell()


cl.qbaseInstallReset(devel=True)

# cl.qbaseLinkToCodeCoreReset("despiegk","dct007")

# result=cl.execute("ls /opt/code")

cl.getConsoles()

from pylabs.Shell import ipshellDebug, ipshell
print "DEBUG NOW main"
ipshell()

q.application.stop()
