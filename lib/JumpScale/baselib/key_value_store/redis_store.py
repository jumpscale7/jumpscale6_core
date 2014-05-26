from store import KeyValueStoreBase

from JumpScale import j

import ujson as json
import lz4
import time

class RedisKeyValueStore(KeyValueStoreBase):

    def __init__(self,namespace="",host='localhost',port=7771,db=0,password='', serializers=[],masterdb=None):

        # import JumpScale.baselib.serializers

        self.redisclient=j.clients.redis.getGeventRedisClient(host, port,password=password)
        self.redisclient.port=port
        self.redisclient.host=host
        self.namespace=""
        KeyValueStoreBase.__init__(self)

        self.masterdb=masterdb

        # if not self.exists("dbsystem", "categories"):
        #     self.categories={"dbsystem":True}
        #     self.set("dbsystem", "categories", {})
        # self.categories=self.get("dbsystem", "categories")

        self.lastchangeIdKey="changelog:%s:lastid"%j.application.whoAmI.gid
        if self.redisclient.get(self.lastchangeIdKey)==None:
            self.redisclient.set(self.lastchangeIdKey,0)
        self.lastchangeId=int(self.redisclient.get(self.lastchangeIdKey))
        self.osis={}
            

    # def serialize(self,data):
    #     from IPython import embed
    #     print "DEBUG NOW ooo"
    #     embed()
        
    #     data=json.dumps(data)
    #     return lz4.dumps(data)
        
    # def unserialize(self,data):
    #     data=lz4.loads(data)
    #     return json.loads(data)

    def deleteChangeLog(self):
        self.masterdb.redisclient.delete("changelog:%s:lastid"%j.application.whoAmI.gid)
        self.masterdb.redisclient.delete("changelog:lastid")
        
        for key in self.masterdb.redisclient.keys("changelog:data:*"):
            self.masterdb.redisclient.delete(key)        

    def checkChangeLog(self):
        """
        @param reset, will just ignore the changelog
        @param delete, means even delete the changelog on master
        """
        print "CHANGELOGCHECK"
        if self.redisclient.get("changelog:lastid")==None:
            return
        lastid=int(self.redisclient.get("changelog:lastid"))
        result=[]
        if lastid>self.lastchangeId:            
            for t in range(self.lastchangeId+1,lastid+1):
                key="changelog:data:%s"%t
                counter=1
                while not self.redisclient.exists(key):
                    time.sleep(0.05)
                    if counter>10:
                        raise RuntimeError("replication error, did not find key %s"%key)
                    counter+=1

                epoch,category,key,action=self.redisclient.get(key).split(":",3)
                counter=1
                key2 = self._getCategoryKey(category, key)
                while not self.redisclient.exists(key2):
                    time.sleep(0.05)
                    if counter>100:
                        raise RuntimeError("replication error, did not find key %s"%key2)
                    counter+=1
                data=self.redisclient.get(key2)
                osis=self.osis[category]
                obj=osis.get(key)
                osis.index(obj.getDictForIndex())

            self.masterdb.redisclient.set(self.lastchangeIdKey,lastid)
            self.lastchangeId=lastid
        return result

    def addToChangeLog(self,category,key,action="M"):        
        if self.masterdb==None: #is master
            t=self.redisclient.incr("changelog:lastid")
            self.redisclient.set("changelog:data:%s"%t,"%s:%s:%s:%s"%(int(time.time()),category,key,action))

    def get(self, category, key):
        categoryKey = self._getCategoryKey(category, key)
        return self.redisclient.get(categoryKey)
        # return self.unserialize(value)

    def set(self, category, key, value,expire=0):
        """
        @param expire is in seconds when value will expire
        """
        # if not self.categories.has_key(category):
        #     self.categories[category]=True
        #     self.set("dbsystem", "categories", self.categories)
        if self.masterdb<>None:
            self.masterdb.set(category,key,value)
        else:
            categoryKey = self._getCategoryKey(category, key)
            self.redisclient.set(categoryKey, value)
            self.addToChangeLog(category, key) #notify system for change                         

    def delete(self, category, key):
        if self.masterdb<>None:
            self.masterdb.delete(category,key)
        else:
            categoryKey = self._getCategoryKey(category, key)
            # self._assertExists(categoryKey)
            self.redisclient.delete(categoryKey)
            self.addToChangeLog(category, key,delete=True)

    def exists(self, category, key):
        categoryKey = self._getCategoryKey(category, key)
        return self.redisclient.exists(categoryKey)

    def list(self, category, prefix):
        from IPython import embed
        print "DEBUG NOW list"
        embed()
        
        return self._stripCategory(fullKeys, category)

    def listCategories(self):
        return self.categories.keys()

    def _stripKey(self, catKey):
        if "." not in catKey:
            raise ValueError("Could not find the category separator in %s" %catKey)
        return catKey.split(".", 1)[0]

    def _getCategoryKey(self, category, key):
        return '%s:%s' % (category, key)

    def _stripCategory(self, keys, category):
        prefix = category + "."
        nChars = len(prefix)
        return [key[nChars:] for key in keys]

    def _categoryExists(self, category):
        categoryKey = self._getCategoryKey(category, "")
        return bool(self._client.prefix(categoryKey, 1))
