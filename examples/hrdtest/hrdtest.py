import os
import struct

from JumpScale import j

j.application.start("hrdtest")

j.system.fs.copyFile("_template.hrd","main.hrd")

hrd=j.core.hrd.getHRD("main.hrd")

print hrd

print "list:"
print hrd.getList("prefix2.list")

print "dict:"
print hrd.getDict("prefix2.dict")


j.application.stop()
