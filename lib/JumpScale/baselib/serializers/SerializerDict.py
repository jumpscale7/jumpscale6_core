
import blosc

class SerializerDict(object):
    def dumps(self,obj):        
        from IPython import embed
        print "DEBUG NOW dict serializer"
        embed()
        
    def loads(self,s):
        return s