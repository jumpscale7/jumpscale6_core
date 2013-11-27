from JumpScale import j
import JumpScale.baselib.remote.cluster.ClusterFactory

j.application.start("deply")

cl = j.remote.cluster.create("test", "test", ["192.168.80.13"], "rooter")

# cl.sshtest()

cl.ubuntuPackageUpdateUpgrade()

cl.qbaseInstallReset(devel=True)

# cl.qbaseLinkToCodeCoreReset("despiegk","dct007")

# result=cl.execute("ls /opt/code")

cl.getConsoles()

j.application.stop()
