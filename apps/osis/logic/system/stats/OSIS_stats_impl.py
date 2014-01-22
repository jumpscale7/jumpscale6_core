from JumpScale import j
from JumpScale.grid.osis.OSISStore import OSISStore

ujson = j.db.serializers.getSerializerType('j')

class mainclass(OSISStore):
    """
    """

    def __init__(self):
        OSISStore.__init__(self)
        # self.elasticsearch=j.core.grid.getstatTargetElasticSearch(esclient=j.core.osis.elasticsearch)        

    def set(self,key,value):
        from IPython import embed
        print "DEBUG NOW stats set"
        embed()
                                      
        return ["",True,True]

    def find(self,query, start=0, size =100):
        raise RuntimeError("osis 'find' for stat not implemented")

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

