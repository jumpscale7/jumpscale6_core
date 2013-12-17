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
        self.elasticsearch=j.core.grid.getstatTargetElasticSearch(esclient=j.core.osis.elasticsearch)        

    def set(self,key,value):
        obj=self.getObject(value)
        self.elasticsearch.index(obj)
        return [obj.key,False,False]

    def find(self,query, start=0, size =100):
        return self.elasticsearch.search(index='system_stat', query=query)

    def destroyindex(self):
        import ipdb
        print "implement destroy of index for stats"
        ipdb.set_trace()                
        
    destroy=destroyindex

    def getIndexName(self):
        return "system_stat"

    def get(self,key):
        j.errorconditionhandler.raiseBug(message="osis get for stat not implemented",category="osis.notimplemented")
        #work with elastic search only

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


      	
