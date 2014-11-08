import os
import struct

from JumpScale import j

j.application.start("hrdtest")

j.system.fs.copyFile("_template.hrd","main.hrd")

hrd=j.core.hrd.getHRD("main.hrd")

print hrd

print "list:"
print hrd.get("prefix2.list")

print "dict:"
ddict= hrd.get("prefix2.dict")
print ddict
ddict["new"]="yes"

hrd.set("prefix2.dict",ddict)
hrd.set("anewkey",ddict)

# hrd.processall()

hrd.save()

hrd=j.core.hrd.getHRD("main.hrd")

if j.system.fs.fileGetContents("main.hrd")==str(hrd):
    print "success"
else:
    print "ERROR"
    print "difference in serialized format & format saved previously on disk"
    j.system.fs.writeFile(filename="main2.hrd",contents=str(hrd))
    j.system.process.executeWithoutPipe("meld main.hrd main2.hrd")

hrd2=j.core.hrd.getHRD("mytestenv")

print hrd2.get("node.n4.servicestoinstall")

j.application.stop()
