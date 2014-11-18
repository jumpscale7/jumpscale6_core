import os
import struct

from JumpScale import j

j.application.start("rsync")

import JumpScale.baselib.rsync


j.system.fs.createDir("/tmp/client")


# def getClient(self,addr="localhost",port=873,login="",passwd=""):
# def getClientSecret(self,addr="localhost",port=873,secret=""):


def test():
    #as authenticated user
    client=j.tools.rsync.getClient(name="jpackages_jumpscale",login="auser",passwd="test")
    client.syncFromServer("","/tmp/jpackages") #will sync all jpackages
    client.syncToServer("/tmp/jpackages","") #will sync all jpackages
# test()

#ofcourse will not work in your case, need to lookup new secret
client=j.tools.rsync.getClientSecret(addr="localhost",port=873,secret="0698df35a7864698a12947030da83c0f")
client.sync("","/tmp/test")

j.application.stop()
