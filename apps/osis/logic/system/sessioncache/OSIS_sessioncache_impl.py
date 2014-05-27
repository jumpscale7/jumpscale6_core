from JumpScale import j
from JumpScale.grid.osis.OSISStore import OSISStore
import JumpScale.grid.grid

ujson = j.db.serializers.getSerializerType('j')

class mainclass(OSISStore):
    TTL = '5d'
    """
    """

    def init(self, path, namespace,categoryname):
        self.initall(path, namespace,categoryname,db=True)
        self.olddb=self.db
        masterdb=j.db.keyvaluestore.getRedisStore(namespace=self.dbprefix, host=j.application.config.get("rediskvs_master_addr"), port=7772, password=j.application.config.get("rediskvs_secret"))
        self.db=j.db.keyvaluestore.getRedisStore(namespace=self.dbprefix, host='localhost', port=7771, password='', masterdb=masterdb, changelog=False)
        self.db.osis[self.dbprefix]=self

    def set(self,key,value,waitIndex=True):
        value = ujson.dumps(value)
        self.db.set(self.dbprefix,key=key,value=value)
        return [key,True,True]

    def destroyindex(self):
        raise NotImplementedError()

    destroy=destroyindex


    def getIndexName(self):
        return "system_sessioncache"

    def get(self,key):
        value =self.db.get(self.dbprefix,key=key)
        if value:
            value = ujson.loads(value)
        return value

    def delete(self, key):
        self.db.delete(self.dbprefix, key)

    def exists(self,key):
        return self.db.exists(self.dbprefix,key=key)

    def setObjIds(self,**args):
        j.errorconditionhandler.raiseBug(message="osis method setObjIds is not relevant for logger namespace",category="osis.notimplemented")

    def rebuildindex(self,**args):
        j.errorconditionhandler.raiseBug(message="osis method rebuildindex is not relevant for logger namespace",category="osis.notimplemented")

    def list(self,**args):
        j.errorconditionhandler.raiseBug(message="osis method list is not relevant for logger namespace",category="osis.notimplemented")


