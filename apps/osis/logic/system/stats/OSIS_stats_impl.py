from JumpScale import j
from JumpScale.grid.osis.OSISStore import OSISStore

ujson = j.db.serializers.getSerializerType('j')
import JumpScale.baselib.graphite

class mainclass(OSISStore):
    """
    """

    def __init__(self):
        OSISStore.__init__(self)
        # self.elasticsearch=j.core.grid.getstatTargetElasticSearch(esclient=j.core.osis.elasticsearch)        

    def set(self,key,value,waitIndex=False):
        out = ""
        if isinstance(value, list):
            for key,val in value:
                out += "%s %s\n" % (key, val)
            key = None
        j.clients.graphite.send(out)
        return [key, False, False]

    def delete(self, key):
        path = '/opt/graphite/storage/whisper/n%s' % key
        if j.system.fs.exists(path):
            j.system.fs.removeDirTree(path)
            return True
        return False

    def find(self,query, start=0, size =100):
        #@todo disabled for now untill we have better solution
        return ""
        return j.clients.graphite.query(query)

    def destroyindex(self):
        raise RuntimeError("osis 'destroyindex' for stat not implemented")

    def getIndexName(self):
        return "system_stats"

    def get(self,key):
        raise RuntimeError("osis 'get' for stat not implemented")

    def exists(self,key):
        raise RuntimeError("osis exists for stat not implemented")
        #work with elastic search only


    #NOT IMPLEMENTED METHODS WHICH WILL NEVER HAVE TO BE IMPLEMENTED

    def setObjIds(self,**args):
        raise RuntimeError("osis method setObjIds is not relevant for stats namespace")

    def rebuildindex(self,**args):
        raise RuntimeError("osis method rebuildindex is not relevant for stats namespace")

    def list(self,**args):
        raise RuntimeError("osis method list is not relevant for stats namespace")

    def removeFromIndex(self,**args):
        raise RuntimeError("osis method removeFromIndex is not relevant for stats namespace")

