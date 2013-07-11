
import struct

class SerializerTime(object):
    def dumps(self,obj):
        struct.pack('<i',o.base.time.getTimeEpoch())
        return obj
    def loads(self,s):
        epoch=struct.unpack('<i', s[0:2])
        return s[2:]