
from OpenWizzy import o

cl=o.core.grid.getZDaemonClientClass()
class OSISClient():
    def __init__(self,ipaddr,port=5544):
        self.client=cl(ipaddr=ipaddr,port=5544,servername="osis")
        self._init()

    def _init(self):
        self.namespaceId2namespaceName,self.categoryId2categoryName,\
            self.namespaceName2namespaceId,self.categoryName2categoryId=self.client.sendcmd("getNameIDsInfoAll")  
            #@todo once in future will have to fetch more specific now fetch all is huge when grid grows (do caching on namespace per namespace basis)

        self._namespaceCategoryCache={}

    def _getIds(self,namespace,category):
        key="%s_%s"%(namespace,category)
        if self._namespaceCategoryCache.has_key(key):
            return self._namespaceCategoryCache[key]
        else:
            if o.basetype.integer.check(namespace):
                namespaceid=namespace
            else:
                if not self.namespaceName2namespaceId.has_key(namespace):
                    self._init()#fetch new namespaces if miss
                    if not self.namespaceName2namespaceId.has_key(namespace):
                        raise RuntimeError("Could not find namespace with name %s"%namespace)
                namespaceid=self.namespaceName2namespaceId[namespace]

            if o.basetype.integer.check(category):
                catid=category
            else:
                if not self.categoryName2categoryId.has_key(category):
                    self._init()#fetch new categories if miss
                    if not self.categoryName2categoryId.has_key(category):
                        raise RuntimeError("Could not find category with name %s"%category)
                catid=self.categoryName2categoryId[category]

            self._namespaceCategoryCache[key]=(namespaceid,catid)
            return self._namespaceCategoryCache[key]

    def set(self,namespace,category,value,key=None,compress=False):
        """
        if key none then key will be given by server
        """
        data = value.getSerializable()
        namespaceid,catid=self._getIds(namespace,category)
        if compress:
            value=o.db.serializers.lzma.dumps(data)
        value=self.client.sendcmd("set",namespaceid=namespaceid,catid=catid,key=key,value=data,compress=compress)
        return value

    def get(self,namespace,category,key,compress=False):
        namespaceid,catid=self._getIds(namespace,category)
        value=self.client.sendcmd("get",namespaceid=namespaceid,catid=catid,key=key,compress=compress)
        if compress:
            value=o.db.serializers.lzma.loads(value)
        return value

    def delete(self,namespace,category,key):
        namespaceid,catid=self._getIds(namespace,category)
        return self.client.sendcmd("delete",namespaceid=namespaceid,catid=catid,key=key)

    def destroy(self,namespace,category):
        namespaceid,catid=self._getIds(namespace,category)
        return self.client.sendcmd("destroy",namespaceid=namespaceid,catid=catid)

    def list(self,namespace,category,prefix=""):
        namespaceid,catid=self._getIds(namespace,category)
        return self.client.sendcmd("list",namespaceid=namespaceid,catid=catid,prefix=prefix)

    def existsNamespace(self,namespacename):
        result=self.listNamespaces(namespacename)
        return len(result)==1

    def search(self,namespace,category,query, start=0, size=10):
        namespaceid,catid=self._getIds(namespace,category)
        return self.client.sendcmd("search",namespaceid=namespaceid,catid=catid,query=query,
            start=start, size=size)

    def createNamespace(self,name=None,template=None,incrementName=False,nsid=0):
        """
        @param if name==None then auto id will be generated and name same as id
        """
        res= self.client.sendcmd("createNamespace",name=name,template=template,incrementName=incrementName,nsid=nsid)
        self._namespaceCategoryCache={}
        return res

    def createNamespaceCategory(self,namespacename,name=None,catid=None):
        """
        Create a category in a namespace
        """
        res = self.client.sendcmd("createNamespaceCategory", namespacename =
                namespacename, name=name, catid = catid)
        self._namespaceCategoryCache = {}
        return res

    def listNamespaces(self,prefix=""):
        return self.client.sendcmd("listNamespaces",prefix=prefix)

    def listNamespaceCategories(self, namespacename):
        return self.client.sendcmd("listNamespaceCategories",
                namespacename = namespacename)


