import os
import struct

from JumpScale import j

j.application.start("hrdtest")

j.system.fs.copyFile("_main.hrd","main.hrd")

print j.core.hrd.getHRD("main.hrd")

j.application.stop()
