
import struct

class SerializerBase64(object):
    def dumps(self,obj):
        obj.encode("base64")
        return obj
    def loads(self,s):
        return s.decode("base64")