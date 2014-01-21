from JumpScale import j
from JumpScale.grid.osis.OSISStore import OSISStore
import JumpScale.grid.grid
import uuid

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
        j.errorconditionhandler.raiseBug(message="osis 'find' for stat not implemented",category="osis.notimplemented")

    def destroyindex(self):
        j.errorconditionhandler.raiseBug(message="osis 'destroyindex' for stat not implemented",category="osis.notimplemented")

    def getIndexName(self):
        return "system_stats"

    def get(self,key):
        j.errorconditionhandler.raiseBug(message="osis 'get' for stat not implemented",category="osis.notimplemented")

    def exists(self,key):
        j.errorconditionhandler.raiseBug(message="osis exists for stat not implemented",category="osis.notimplemented")
        #work with elastic search only


    #NOT IMPLEMENTED METHODS WHICH WILL NEVER HAVE TO BE IMPLEMENTED

    def setObjIds(self,**args):
        j.errorconditionhandler.raiseBug(message="osis method setObjIds is not relevant for statger namespace",category="osis.notimplemented")

    def rebuildindex(self,**args):
        j.errorconditionhandler.raiseBug(message="osis method rebuildindex is not relevant for statger namespace",category="osis.notimplemented")

    def list(self,**args):
        j.errorconditionhandler.raiseBug(message="osis method list is not relevant for statger namespace",category="osis.notimplemented")

    def removeFromIndex(self,**args):
        j.errorconditionhandler.raiseBug(message="osis method removeFromIndex is not relevant for statger namespace",category="osis.notimplemented")

