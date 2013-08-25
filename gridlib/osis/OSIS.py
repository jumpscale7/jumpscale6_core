from JumpScale import j
import JumpScale.baselib.elasticsearch


class OSIS:

    """
    """

    def __init__(self):
        self.osisInstances = {}  # key is namespaceid_categoryid
        self.namespaceId2namespaceName = {}
        self.categoryId2categoryName = {}
        self.namespaceName2namespaceId = {}
        self.categoryName2categoryId = {}
        self.db = None  # default db
        self.elasticsearch = None  # default elastic search connection
        self.loadCoreHRD()

    def loadCoreHRD(self):
        idpath = j.system.fs.joinPaths('cfg', 'id.hrd')
        if not j.system.fs.exists(idpath):
            idcontent = "namespace.lastid=10"  # start at 10
            j.system.fs.writeFile(idpath, idcontent)
        self.corehrd = j.core.hrd.getHRDTree("cfg")

    def get(self, namespaceid, categoryid):
        fullname = "%s_%s" % (namespaceid, categoryid)
        if self.osisInstances.has_key(fullname):
            return self.osisInstances[fullname]
        j.errorconditionhandler.raiseBug(
            message="cannot find osis local instance for namespaceid:%s & categoryid:%s" % (namespaceid, categoryid), category="osis.valueerror")

    def getFromName(self, namespaceName, categoryName):
        namespaceid = self.namespaceName2namespaceId[namespaceName]
        categoryid = self.categoryName2categoryId[categoryName]
        return self.get(namespaceid, categoryid)

    def incrementNamespaceId(self):
        lastid = self.corehrd.getInt("namespace.lastid") + 1
        if lastid < 10:
            lastid = 11
        self.corehrd.set("namespace.lastid", lastid)
        return lastid

    def createNamespace(self, name=None, incrementName=False, nsid=0, template=None):
        """
        @param if name==None then auto id will be generated and name same as id
        """
        if name == None:
            name = str(self.incrementNamespaceId())
            id = int(name)
        elif incrementName and nsid == 0:
            id = self.incrementNamespaceId()
            name += str(id)
        elif incrementName and nsid <> 0:
            id = nsid
            name += str(id)
        else:
            id = None

        j.system.fs.createDir(j.system.fs.joinPaths(self.path, name))
        if template <> None:
            j.system.fs.copyDirTree(j.system.fs.joinPaths(self.path, "_%s" % template), j.system.fs.joinPaths(self.path, name), overwriteFiles=False)
            j.system.fs.remove(j.system.fs.joinPaths(self.path, name, "namespace.hrd"))
            j.system.fs.remove(j.system.fs.joinPaths(self.path, name, "namespaceid.hrd"))

        path = j.system.fs.joinPaths(self.path, name)
        if id <> None:
            self._initDefaultContent(overwriteHRD=False, namespacename=name)
            hrd = j.core.hrd.getHRDTree(path)
            hrd.set("namespace.id", id)

        self.init(path=self.path, overwriteHRD=False, namespacename=name, template=template)

        return [name, id]

    def listNamespaces(self, prefix=""):
        ddirs = j.system.fs.listDirsInDir(self.path, dirNameOnly=True)
        if prefix != "":
            ddirs = [item for item in ddirs if item.find(prefix) == 0]
        return ddirs

    def listNamespaceCategories(self, namespacename):
        ddirs = j.system.fs.listDirsInDir(j.system.fs.joinPaths(self.path,
                                                                namespacename), dirNameOnly=True)
        return ddirs

    def createNamespaceCategory(self, namespacename, name=None, catid=None):
        """
        @param if name==None then auto id will be generated and name same as id
        """
        namespacepath = j.system.fs.joinPaths(self.path, namespacename)
        if not j.system.fs.exists(path=namespacepath):
            self.createNamespace(namespacename)
        j.system.fs.createDir(j.system.fs.joinPaths(namespacepath, name))
        if catid <> None:
            self._initDefaultContent(overwriteHRD=False, overwriteTasklets=False, namespacename=namespacename)
            catpath = j.system.fs.joinPaths(self.path, namespacename, name)
            hrd = j.core.hrd.getHRDTree(catpath)
            hrd.set("category.id", catid)
        self.init(path=self.path, overwriteHRD=False, overwriteImplementation=False, namespacename=namespacename)

    def _initDefaultContent(self, overwriteHRD=False, namespacename=None):
        path = self.path
        if namespacename == None:
            for namespacename in j.system.fs.listDirsInDir(path, dirNameOnly=True):
                self._initDefaultContent(overwriteHRD, namespacename=namespacename)

        else:
            templatespath = "_templates"
            templatespath_namespace = j.system.fs.joinPaths(templatespath, "namespace")
            templatespath_category = j.system.fs.joinPaths(templatespath, "category")
            namespacepath = j.system.fs.joinPaths(path, namespacename)
            j.system.fs.copyDirTree(templatespath_namespace, namespacepath, overwriteFiles=overwriteHRD)
            if namespacename[0] <> "_" and j.system.fs.exists(path=j.system.fs.joinPaths(namespacepath, ".parentInTemplate")):  # check if parent is coming from template
                j.system.fs.remove(j.system.fs.joinPaths(namespacepath, "OSIS_parent.py"))
                j.system.fs.remove(j.system.fs.joinPaths(namespacepath, "OSIS_parent.pyc"))

            for catname in j.system.fs.listDirsInDir(namespacepath, dirNameOnly=True):
                catpath = j.system.fs.joinPaths(namespacepath, catname)
                j.system.fs.copyDirTree(templatespath_category, catpath, overwriteFiles=overwriteHRD)
                # j.system.fs.copyDirTree(templatespath_osistasklets,catpath,overwriteFiles=overwriteTasklets)

    def init(self, path="", overwriteHRD=False, overwriteImplementation=False, namespacename=None, template=None):

        if path == "":
            path = "logic"

        self.path = path

        j.logger.consoleloglevel = 7

        if namespacename == None:
            for namespacename in j.system.fs.listDirsInDir(path, dirNameOnly=True):
                self.init(path, overwriteHRD, overwriteImplementation, namespacename=namespacename)

        else:

            # te=j.core.taskletengine.get(j.system.fs.joinPaths("systemtasklets","init"))
            # te.executeV2(osis=self) #will add db & elasticsearch w
            if namespacename[0] == "_":
                return
            self._initDefaultContent(overwriteHRD, namespacename=namespacename)
            hrd = self.corehrd
            hrd.add2tree(path)
            hrd2 = hrd.getHrd("")

            # enable db's
            if hrd2.osis_db_type == "filesystem":
                self.db = j.db.keyvaluestore.getFileSystemStore("osis")
            else:
                raise RuntimeError("Only filesystem db implemented in osis")

            # wait for elastic search & get
            self.elasticsearch = j.clients.elasticsearch.get(ip=hrd2.osis_elasticsearch_ip, port=int(hrd2.osis_elasticsearch_port))
            j.core.osis.db = self.db
            j.core.osis.elasticsearch = self.elasticsearch

            namespacepath = j.system.fs.joinPaths(path, namespacename)
            hrdNameSpace = hrd.getHrd("%s" % (namespacename))
            if not hrdNameSpace.get("namespace.id", True):  # cannot be getInt because 0 is valid for system namespace
                hrdNameSpace.set("namespace.id", self.incrementNamespaceId())

            if not hrdNameSpace.get("namespace.name", True):
                hrdNameSpace.set("namespace.name", namespacename)

            namespaceid = hrdNameSpace.getInt("namespace.id")
            self.namespaceId2namespaceName[namespaceid] = namespacename
            self.namespaceName2namespaceId[namespacename] = namespaceid

            if template <> None:
                hrdNameSpace.set("namespace.type", template)

            for catname in j.system.fs.listDirsInDir(namespacepath, dirNameOnly=True):
                hrdCat = hrd.getHrd("%s/%s" % (namespacename, catname))
                catpath = j.system.fs.joinPaths(namespacepath, catname)
                catid = hrdCat.getInt("category.id")
                if catid == 0:
                    # need to find id for category
                    catid = hrdNameSpace.getInt("category.lastid") + 1
                    hrdNameSpace.set("category.lastid", catid)
                    hrdCat.set("category.id", catid)

                if hrdCat.get("category.name") == "":
                    hrdCat.set("category.name", catname)

                self.categoryId2categoryName[catid] = catname
                self.categoryName2categoryId[catname] = catid

                key = "%s_%s" % (namespaceid, catid)

                # check if there is already an implfile
                implfile = "OSIS_%s_impl.py" % catname
                implpath = j.system.fs.joinPaths(catpath, implfile)
                fileFrom = j.system.fs.joinPaths(namespacepath, "OSIS_category_template.py")
                if overwriteImplementation or not j.system.fs.exists(path=implpath):
                    j.system.fs.copyFile(fileFrom, implpath)

                classs = j.core.osis._loadModuleClass(implpath)
                if namespacename[0] <> "_":
                    osis = classs()
                    osis.init(catpath, hrdCat)
                    self.osisInstances[key] = osis

            j.core.osis.db = None
            j.core.osis.elasticsearch = None
