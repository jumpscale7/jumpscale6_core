from OpenWizzy import o
from OpenWizzy.grid.osis.OSISStore import OSISStore
import uuid
class mainclass(OSISStore):
    """
    """

    def __init__(self):
        OSISStore.__init__(self)
        self.eslogclient=o.core.grid.getLogTargetElasticSearch(esclient=o.core.osis.elasticsearch)        

    def set(self,key,value):
        docs = []
        for logobject in q.db.serializers.ujson.loads(value):
            logobject["id"] = "%s_%s_%s_%s"%(logobject["gid"], logobject["bid"], logobject["pid"], logobject["order"])            
            docs.append(logobject)

        print "batch:%s"%len(docs)            
        #self.elasticsearch.bulk_index(index="clusterlog_%s_%s"%(logobject["bid"],logobject["gid"]), doc_type="json", docs=docs, id_field="id")                        
        self.elasticsearch.bulk_index(index="clusterlog", doc_type="json", docs=docs, id_field="id")                        
        return ["",True,True]

    def get(self,key):
        q.errorconditionhandler.raiseBug(message="osis get for log not implemented",category="osis.notimplemented")
        #work with elastic search only

    def exists(self,key):
        q.errorconditionhandler.raiseBug(message="osis exists for log not implemented",category="osis.notimplemented")
        #work with elastic search only

    def find(self,query, start = 0, size = 10):
        q.errorconditionhandler.raiseBug(message="osis find for log not implemented",category="osis.notimplemented")
        #work with elastic search only

    def destroyindex(self):
        q.errorconditionhandler.raiseBug(message="osis destroyindex for log not implemented",category="osis.notimplemented")
        #work with elastic search only  

    def destroy(self):
        return self.destroyindex()

    def getIndexName(self):
        return "clusterlog"


    #NOT IMPLEMENTED METHODS WHICH WILL NEVER HAVE TO BE IMPLEMENTED

    def setObjIds(self,**args):
        q.errorconditionhandler.raiseBug(message="osis method setObjIds is not relevant for logger namespace",category="osis.notimplemented")

    def rebuildindex(self,**args):
        q.errorconditionhandler.raiseBug(message="osis method rebuildindex is not relevant for logger namespace",category="osis.notimplemented")

    def list(self,**args):
        q.errorconditionhandler.raiseBug(message="osis method list is not relevant for logger namespace",category="osis.notimplemented")

    def removeFromIndex(self,**args):
        q.errorconditionhandler.raiseBug(message="osis method removeFromIndex is not relevant for logger namespace",category="osis.notimplemented")

