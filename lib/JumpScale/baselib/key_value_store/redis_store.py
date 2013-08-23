from store import KeyValueStoreBase

from JumpScale import j


class RedisKeyValueStore(KeyValueStoreBase):

    def __init__(self,namespace="",host='localhost',port=6379,db=0,key='', serializers=[]):

        self.redisclient=j.clients.redis.get(host, port, db=db, key=key)
        self.db = self.redisclient.redis
        self.namespace=""
        KeyValueStoreBase.__init__(self)

        if not self.exists("dbsystem", "categories"):
            self.categories={"dbsystem":True}
            self.set("dbsystem", "categories", {})
        self.categories=self.get("dbsystem", "categories")

    def get(self, category, key):
        #self._assertExists(category, key)
        categoryKey = self._getCategoryKey(category, key)
        value = self.db.get(categoryKey)
        return self.unserialize(value)

    def set(self, category, key, value, expire=0):
        """
        @param expire is in seconds when value will expire
        """
        if not self.categories.has_key(category):
            self.categories[category]=True
            self.set("dbsystem", "categories", self.categories)
        categoryKey = self._getCategoryKey(category, key)
        self.db.set(categoryKey, self.serialize(value))
        if expire<>0:
            self.db.expire(categoryKey,expire)

    def delete(self, category, key):
        self._assertExists(category, key)

        categoryKey = self._getCategoryKey(category, key)
        self._client.delete(categoryKey)

    def exists(self, category, key):
        categoryKey = self._getCategoryKey(category, key)
        return self.db.exists(categoryKey)

    def list(self, category, prefix):
        raise RuntimeError("redis list not implemented")
        categoryKey = self._getCategoryKey(category, prefix)
        fullKeys = self._client.prefix(categoryKey)
        return self._stripCategory(fullKeys, category)

    def listCategories(self):
        return self.categories.keys()

    def _stripKey(self, catKey):
        if "." not in catKey:
            raise ValueError("Could not find the category separator in %s" %catKey)
        return catKey.split(".", 1)[0]

    def _getCategoryKey(self, category, key):

        return '%s.%s' % (category, key)

    def _stripCategory(self, keys, category):
        prefix = category + "."
        nChars = len(prefix)
        return [key[nChars:] for key in keys]

    def _categoryExists(self, category):
        categoryKey = self._getCategoryKey(category, "")
        return bool(self._client.prefix(categoryKey, 1))
