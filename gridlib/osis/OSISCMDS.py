from OpenWizzy import o
from OpenWizzy.grid.grid.ZDaemon import ZDaemonCMDS

class OSISCMDS(ZDaemonCMDS):
    def __init__(self,daemon):
        self.daemon=daemon
        self.osis=None

    def getNameIDsInfoAll(self):
        ids=[self.osis.namespaceId2namespaceName,
            self.osis.categoryId2categoryName,
            self.osis.namespaceName2namespaceId,
            self.osis.categoryName2categoryId]
        return ids

    def createNamespace(self,name=None,incrementName=False,nsid=0,template=None):
        """
        @param if name==None then auto id will be generated and name same as id
        """
        return self.osis.createNamespace(name=name,incrementName=incrementName,nsid=nsid,template=template)

    def createNamespaceCategory(self,namespacename,name=None,catid=None):
        """
        Create namespace Category
        """
        return self.osis.createNamespaceCategory(namespacename = namespacename,
                name = name, catid = catid)

    def listNamespaces(self,prefix=""):
        return self.osis.listNamespaces(prefix)

    def listNamespaceCategories(self, namespacename):
        return self.osis.listNamespaceCategories(namespacename)


    def get(self,namespaceid,catid,key,compress):
        oi=self.osis.get(namespaceid,catid)
        return oi.get(key)        

    def set(self,namespaceid,catid,key,value,compress):
        oi=self.osis.get(namespaceid,catid)
        return oi.set(key=key,value=value)

    def delete(self,namespaceid,catid,key):
        oi=self.osis.get(namespaceid,catid)
        return oi.delete(key=key)

    def search(self, namespaceid, catid, query, start=0, size=10):
        oi = self.osis.get(namespaceid, catid)
        result = oi.find(query, start, size)
        return result 

    def list(self, namespaceid, catid, prefix):
        oi = self.osis.get(namespaceid, catid)
        return oi.list(prefix)

    def log(self,log):
        #in future should use bulk upload feature, now 1 by 1
        print log["message"]

    def pingcmd(self):
        return "pong"

    def echo(self,msg=""):
        return msg
