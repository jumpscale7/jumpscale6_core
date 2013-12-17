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
        self.elasticsearch=j.core.grid.getLogTargetElasticSearch(esclient=j.core.osis.elasticsearch)        

    def set(self,key,value):
        docs = []
        for logobject in ujson.loads(value):
            logobject["id"] = "%s_%s_%s"%(logobject["gid"], logobject["pid"], logobject["order"])            
            docs.append(logobject)

        # print "batch:%s"%len(docs)            
        #self.elasticsearch.bulk_index(index="clusterlog_%s_%s"%(logobject["bid"],logobject["gid"]), doc_type="json", docs=docs, id_field="id")                        
        self.elasticsearch.bulk_index(index="system_log", doc_type="json", docs=docs, id_field="id")                        
        return ["",True,True]

    def find(self,query, start=0, size =100):
        return self.elasticsearch.search(index='system_log', query=query)

    def destroyindex(self):
        import ipdb
        print "implement destroy of index for logs"
        ipdb.set_trace()
        
    destroy=destroyindex


    def getIndexName(self):
        return "system_log"

    def get(self,key):
        j.errorconditionhandler.raiseBug(message="osis get for log not implemented",category="osis.notimplemented")
        #work with elastic search only

    def exists(self,key):
        j.errorconditionhandler.raiseBug(message="osis exists for log not implemented",category="osis.notimplemented")
        #work with elastic search only


    #NOT IMPLEMENTED METHODS WHICH WILL NEVER HAVE TO BE IMPLEMENTED

    def setObjIds(self,**args):
        j.errorconditionhandler.raiseBug(message="osis method setObjIds is not relevant for logger namespace",category="osis.notimplemented")

    def rebuildindex(self,**args):
        j.errorconditionhandler.raiseBug(message="osis method rebuildindex is not relevant for logger namespace",category="osis.notimplemented")

    def list(self,**args):
        j.errorconditionhandler.raiseBug(message="osis method list is not relevant for logger namespace",category="osis.notimplemented")

    def removeFromIndex(self,**args):
        j.errorconditionhandler.raiseBug(message="osis method removeFromIndex is not relevant for logger namespace",category="osis.notimplemented")

