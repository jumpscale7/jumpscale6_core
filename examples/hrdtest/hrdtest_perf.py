import os
import struct

from JumpScale import j

j.application.start("hrdtest")

print "start"
j.base.timer.start()
nr=1000
for i in range(nr):
    hrd2=j.core.hrd.getHRD("mytestenv")
    hrd2.get("node.n4.servicestoinstall")
j.base.timer.stop(nr)

j.application.stop()
