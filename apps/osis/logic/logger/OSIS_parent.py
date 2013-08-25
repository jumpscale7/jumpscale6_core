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
        self.eslogclient=j.core.grid.getLogTargetElasticSearch(esclient=j.core.osis.elasticsearch)        

    def set(self,key,value):
        docs = []
        for logobject in ujson.loads(value):
            logobject["id"] = "%s_%s_%s_%s"%(logobject["gid"], logobject["bid"], logobject["pid"], logobject["order"])            
            docs.append(logobject)

        print "batch:%s"%len(docs)            
        #self.elasticsearch.bulk_index(index="clusterlog_%s_%s"%(logobject["bid"],logobject["gid"]), doc_type="json", docs=docs, id_field="id")                        
        self.elasticsearch.bulk_index(index="clusterlog", doc_type="json", docs=docs, id_field="id")                        
        return ["",True,True]

    def get(self,key):
        o.errorconditionhandler.raiseBug(message="osis get for log not implemented",category="osis.notimplemented")
        #work with elastic search only

    def exists(self,key):
        o.errorconditionhandler.raiseBug(message="osis exists for log not implemented",category="osis.notimplemented")
        #work with elastic search only

    def find(self,query, start = 0, size = 10):
        o.errorconditionhandler.raiseBug(message="osis find for log not implemented",category="osis.notimplemented")
        #work with elastic search only

    def destroyindex(self):
        o.errorconditionhandler.raiseBug(message="osis destroyindex for log not implemented",category="osis.notimplemented")
        #work with elastic search only  

    def destroy(self):
        return self.destroyindex()

    def getIndexName(self):
        return "clusterlog"


    #NOT IMPLEMENTED METHODS WHICH WILL NEVER HAVE TO BE IMPLEMENTED

    def setObjIds(self,**args):
        o.errorconditionhandler.raiseBug(message="osis method setObjIds is not relevant for logger namespace",category="osis.notimplemented")

    def rebuildindex(self,**args):
        o.errorconditionhandler.raiseBug(message="osis method rebuildindex is not relevant for logger namespace",category="osis.notimplemented")

    def list(self,**args):
        o.errorconditionhandler.raiseBug(message="osis method list is not relevant for logger namespace",category="osis.notimplemented")

    def removeFromIndex(self,**args):
        o.errorconditionhandler.raiseBug(message="osis method removeFromIndex is not relevant for logger namespace",category="osis.notimplemented")

