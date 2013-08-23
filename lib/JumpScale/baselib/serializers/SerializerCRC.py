
import struct

class SerializerCRC(object):
    def dumps(self,obj):
        o.tools.hash.crc32_string(obj)
        return obj
    def loads(self,s):
        return s[4:]