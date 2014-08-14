from JumpScale import j
from JumpScale.grid.osis.OSISStoreES import OSISStoreES
import JumpScale.grid.grid
import uuid

ujson = j.db.serializers.getSerializerType('j')

class mainclass(OSISStoreES):
    TTL = '5d'
    """
    """

    def set(self,key,value,waitIndex=False):
        ##no manipulation so no longer needed
        # docs = []
        # for logobject in value:            
        #     docs.append(logobject)

        # print "batch log:%s"%len(value)            
        #self.elasticsearch.bulk_index(index="clusterlog_%s_%s"%(logobject["bid"],logobject["gid"]), doc_type="json", docs=docs, id_field="id")                                                    
        if len(value)>0:
            for log in value:
                log['_ttl'] = self.TTL
            self.elasticsearch.bulk_index(index="system_log", doc_type="json", docs=value, id_field="guid")
        return ["",True,True]

    def find(self, query, start=0, size=100):
        kwargs = dict()
        if start:
            kwargs['es_from'] = start
        if size:
            kwargs['size'] = size
        try:
            return self.elasticsearch.search(index='system_log', query=query, **kwargs)
        except:
            return {'hits': {'hits': list(), 'total': 0}}

    def destroyindex(self):
        raise NotImplementedError()
        
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


