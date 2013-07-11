from pylabs.InitBase import *
import os

import time
import struct

q.application.appname = "test"
q.application.start()


from ZObjects import *

oo2=ZAction(name="asda sdasdas",code="asdasd asda sd asd asd asd asd asd as d",path="asda sd asda sd asd asd ",category="asd asd asd as", errordescr="asd asd asd asd asd ",\
            recoverydescr="dsfsadfgsdsdfgsdfgsdfgs", maxtime=45,masterid=453)

ooo=q.db.serializers.ujson.dumps(oo2)


def serialize4disk(objstr,id=0):
    return struct.pack("<ii",5454454,id)+objstr

def unserialize4disk(data):
    """
    @return epoch,id,objstr
    """
    return struct.unpack_from("<i",data,0)[0],struct.unpack_from("<i",data,4)[0],data[8:]

nr=100000
start=time.time()
for i in range(nr):
    data=serialize4disk(ooo,i)
    epoch,id,objstr=unserialize4disk(data)
    if objstr<>ooo:
        raise RuntimeError("serialization failed")
print "stop"
stop=time.time()
print "nrsec:%s" % str(float(nr)/(float(stop)-float(start)))

from pylabs.Shell import ipshellDebug,ipshell
print "DEBUG NOW id"
ipshell()

q.application.stop()