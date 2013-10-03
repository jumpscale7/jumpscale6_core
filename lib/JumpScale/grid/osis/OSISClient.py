
from JumpScale import j
import JumpScale.grid.zdaemon

class OSISClient():

    def __init__(self, addr, port=5544):
        self.client = j.core.zdaemon.getZDaemonClient(addr=addr, port=5544, category="osis")
        self._init()

    def _init(self):
        self.namespaceId2namespaceName, self.namespaceName2namespaceId = self.client.getNameIDsInfoAll()
            #@todo once in future will have to fetch more specific now fetch all is huge when grid grows (do caching on namespace per namespace basis)

        self._namespaceCategoryCache = {}
        for namespacename, categorymap in self.namespaceName2namespaceId.iteritems():
            for categoryname, ids in categorymap.iteritems():
                key = "%s_%s" % (namespacename, categoryname)
                self._namespaceCategoryCache[key] = ids

    def _getIds(self, namespace, category):
        if j.basetype.integer.check(namespace) and j.basetype.integer.check(category):
            return namespace, category
        key = "%s_%s" % (namespace, category)
        ids = self._namespaceCategoryCache.get(key)
        if not ids:
            # maybe category is new lets try to refetch
            self._init()
            ids = self._namespaceCategoryCache.get(key)
            if not ids:
                raise RuntimeError("Could not find category [%s] in namepsace [%s]" % (category, namespace))
        return ids 

    def set(self, namespace, category, value, key=None, compress=False):
        """
        if key none then key will be given by server
        """
        if isinstance(value, str):
            data = value
        else:
            data = value.getSerializable()
        namespaceid, catid = self._getIds(namespace, category)
        if compress:
            value = j.db.serializers.lzma.dumps(data)
        value = self.client.set(namespaceid=namespaceid, catid=catid, key=key, value=data, compress=compress)
        return value

    def get(self, namespace, category, key, compress=False):
        namespaceid, catid = self._getIds(namespace, category)
        value = self.client.get(namespaceid=namespaceid, catid=catid, key=key, compress=compress)
        if compress:
            value = j.db.serializers.lzma.loads(value)
        return value

    def delete(self, namespace, category, key):
        namespaceid, catid = self._getIds(namespace, category)
        return self.client.delete(namespaceid=namespaceid, catid=catid, key=key)

    def destroy(self, namespace, category):
        namespaceid, catid = self._getIds(namespace, category)
        return self.client.destroy(namespaceid=namespaceid, catid=catid)

    def list(self, namespace, category, prefix=""):
        namespaceid, catid = self._getIds(namespace, category)
        return self.client.list(namespaceid=namespaceid, catid=catid, prefix=prefix)

    def existsNamespace(self, namespacename):
        result = self.listNamespaces(namespacename)
        return len(result) == 1

    def search(self, namespace, category, query, start=0, size=None):
        if j.basetype.dictionary.check(query):
            query = j.db.serializers.ujson.dumps(query)
        namespaceid, catid = self._getIds(namespace, category)
        return self.client.search(namespaceid=namespaceid, catid=catid, query=query,
                                  start=start, size=size)

    def createNamespace(self, name=None, template=None, incrementName=False, nsid=0):
        """
        @param if name==None then auto id will be generated and name same as id
        """
        res = self.client.createNamespace(name=name, template=template, incrementName=incrementName, nsid=nsid)
        self._namespaceCategoryCache = {}
        return res

    def createNamespaceCategory(self, namespacename, name=None, catid=None):
        """
        Create a category in a namespace
        """
        res = self.client.createNamespaceCategory(namespacename=
                                                  namespacename, name=name, catid=catid)
        self._namespaceCategoryCache = {}
        return res

    def listNamespaces(self, prefix=""):
        return self.client.listNamespaces(prefix=prefix)

    def listNamespaceCategories(self, namespacename):
        return self.client.listNamespaceCategories(namespacename=namespacename)
